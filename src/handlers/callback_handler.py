from telethon import events
from src.config import setup_logger

class CallbackHandler:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.logger = setup_logger('CallbackHandler')

    def register_handlers(self):
        @self.client.on(events.CallbackQuery())
        async def handle_callback(event):
            """Handle button callbacks."""
            try:
                self.logger.info(f"Callback data received: {event.data}")

                # Ensure we fetch the original message
                original_message = await event.get_message()
                data = event.data.decode("utf-8")


                if data == "send_to_target":
                    self.logger.info("User chose to send video to target chat.")
                    # Forward the video to the target chat
                    await self.client.send_file(
                        self.config.chat_target,
                        original_message.media,
                        parse_mode='markdown',
                        supports_streaming=True,
                        spoiler=True
                      )
                    # Borrar el video del chat del usuario
                    await original_message.delete()  # Delete after sending
                elif data == "discard":
                    # Delete the video from the user's chat
                    await original_message.delete()  # Use the fetched message
                    await event.answer("Video descartado y eliminado.")
                else:
                    await event.answer("Acción desconocida.")
            except Exception as e:
                self.logger.error(f"Error handling callback: {e}")