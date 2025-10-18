import cv2
import torch
from transformers import DetrImageProcessor, DetrForObjectDetection, ViTImageProcessor, ViTForImageClassification
import numpy as np
from PIL import Image
import sys
import os
import logging
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directory to save detected frames
DETECTIONS_DIR = "/app/detections"
os.makedirs(DETECTIONS_DIR, exist_ok=True)

def load_models():
    logger.info("Loading models...")
    # Load DETR for person detection
    processor_detr = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
    model_detr = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

    # Load NSFW classifier
    processor_nsfw = ViTImageProcessor.from_pretrained("AdamCodd/vit-base-nsfw-detector")
    model_nsfw = ViTForImageClassification.from_pretrained("AdamCodd/vit-base-nsfw-detector")

    logger.info("Models loaded successfully.")
    return processor_detr, model_detr, processor_nsfw, model_nsfw

def detect_persons(image, processor, model):
    logger.debug("Detecting persons in image...")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    # Convert outputs to COCO API
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)[0]

    persons = []
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        if model.config.id2label[label.item()] == "person":
            persons.append(box.tolist())
    logger.debug(f"Detected {len(persons)} persons.")
    return persons

def classify_nsfw(image, processor, model):
    logger.debug("Classifying NSFW content...")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits

    # Model predicts one of the classes
    predicted_class_idx = logits.argmax(-1).item()
    predicted_class = model.config.id2label[predicted_class_idx]

    # Get probabilities
    probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]
    nsfw_prob = probabilities[predicted_class_idx].item()

    # Log all probabilities
    all_probs = {model.config.id2label[i]: prob.item() for i, prob in enumerate(probabilities)}
    logger.debug(f"All NSFW probabilities: {all_probs}")

    # Consider NSFW if class is 'nsfw'
    is_nsfw = predicted_class.lower() == 'nsfw'

    logger.debug(f"Classification: {predicted_class} (prob: {nsfw_prob:.2f}), NSFW: {is_nsfw}")
    return is_nsfw, predicted_class, nsfw_prob

def analyze_video(video_path, num_random_frames=10, context_frames=5):
    logger.info(f"Starting video analysis for {video_path}")
    if not os.path.exists(video_path):
        logger.error(f"Video file {video_path} not found.")
        return False, False

    processor_detr, model_detr, processor_nsfw, model_nsfw = load_models()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("Could not open video file.")
        return False, False

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info(f"Video has {total_frames} frames.")

    if total_frames == 0:
        logger.error("Video has no frames.")
        cap.release()
        return False, False

    # Select random frame numbers
    random_frames = sorted(random.sample(range(1, total_frames + 1), min(num_random_frames, total_frames)))
    logger.info(f"Checking random frames: {random_frames}")

    persons_detected = False
    nsfw_detected = False
    person_frame = None

    # First pass: check random frames for persons
    for frame_num in random_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num - 1)  # 0-based
        ret, frame = cap.read()
        if not ret:
            logger.warning(f"Could not read frame {frame_num}")
            continue

        logger.debug(f"Processing frame {frame_num}")

        # Convert BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image)

        # Detect persons
        persons = detect_persons(pil_image, processor_detr, model_detr)
        if persons:
            persons_detected = True
            person_frame = frame_num
            logger.info(f"Persons detected in frame {frame_num}, switching to context analysis.")
            break

    if not persons_detected:
        cap.release()
        logger.info("No persons detected in random frames.")
        return False, False

    # Second pass: check NSFW in context frames around the person_frame
    start_frame = max(1, person_frame - context_frames)
    end_frame = min(total_frames, person_frame + context_frames)
    context_frame_nums = list(range(start_frame, end_frame + 1))
    logger.info(f"Checking NSFW in context frames: {context_frame_nums}")

    for frame_num in context_frame_nums:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num - 1)
        ret, frame = cap.read()
        if not ret:
            continue

        logger.debug(f"Checking NSFW in frame {frame_num}")

        # Convert BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image)

        # Detect persons again to get bounding boxes
        persons = detect_persons(pil_image, processor_detr, model_detr)
        if not persons:
            continue  # No persons in this frame

        # For each person, crop, classify, and save
        for i, box in enumerate(persons):
            x1, y1, x2, y2 = map(int, box)
            cropped = pil_image.crop((x1, y1, x2, y2))
            if cropped.size[0] == 0 or cropped.size[1] == 0:
                continue

            # Save the person crop
            person_filename = f"{DETECTIONS_DIR}/person_frame_{frame_num}_person_{i}.png"
            cropped.save(person_filename)
            logger.debug(f"Saved person crop to {person_filename}")

            # Classify NSFW on crop
            is_nsfw, pred_class, prob = classify_nsfw(cropped, processor_nsfw, model_nsfw)
            if is_nsfw:
                nsfw_detected = True
                # Save additional NSFW versions if needed
                crop_filename = f"{DETECTIONS_DIR}/nsfw_crop_frame_{frame_num}_person_{i}_class_{pred_class}_prob_{prob:.2f}.png"
                cropped.save(crop_filename)
                # Save the full frame
                frame_filename = f"{DETECTIONS_DIR}/nsfw_frame_{frame_num}_class_{pred_class}_prob_{prob:.2f}.png"
                pil_image.save(frame_filename)
                logger.warning(f"NSFW content detected in frame {frame_num}, saved crop to {crop_filename} and frame to {frame_filename}: {pred_class} with prob {prob:.2f}")
                break  # Stop if NSFW found

        if nsfw_detected:
            break

    cap.release()
    logger.info(f"Analysis completed. Persons: {persons_detected}, NSFW: {nsfw_detected}")
    return persons_detected, nsfw_detected

if __name__ == "__main__":
    logger.info("Script started.")
    if len(sys.argv) < 2:
        logger.error("Usage: python person_detector.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    logger.info(f"Analyzing video: {video_path}")
    persons, nsfw = analyze_video(video_path)
    logger.info("Script finished.")
    print(f"Persons detected: {persons}")
    print(f"NSFW detected: {nsfw}")
