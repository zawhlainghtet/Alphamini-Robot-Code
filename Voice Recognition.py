import asyncio
import logging
import mini.mini_sdk as Mini

from mini.apis.api_observe import ObserveSpeechRecognise
from mini.apis.api_sound import StartPlayTTS
from mini.dns.dns_browser import WiFiDevice
from mini.pb2.codemao_speechrecognise_pb2 import SpeechRecogniseResponse

# Set logging level for debugging
Mini.set_log_level(logging.DEBUG)
Mini.set_robot_type(Mini.RobotType.EDU)

async def play_tts(text: str):
    """Plays text using Text-to-Speech (TTS)."""
    block = StartPlayTTS(text=text)
    response = await block.execute()

    if isinstance(response, tuple) and len(response) == 2:
        result, message = response  # Unpack tuple
        print(f'TTS Response: {result}, Message: {message}')
    else:
        print(f'Unexpected TTS Response Format: {response}')

async def test_speech_recognise():
    """Monitor voice recognition demo"""
    observe = ObserveSpeechRecognise()

    async def handler(msg: SpeechRecogniseResponse):
        recognized_text = str(msg.text).strip().lower()
        print(f'Raw Speech Recognition Output: "{recognized_text}"')

        if recognized_text == "hello.":
            print("Recognized 'Hello', responding with TTS...")
            asyncio.create_task(play_tts("Hello, I am AlphaMini! How can I assist you?"))

        elif recognized_text == "stop.":
            print("Recognized 'Stop', stopping speech recognition...")
            asyncio.create_task(play_tts("Hello, I will stop to assist you"))
            

    observe.set_handler(lambda msg: asyncio.create_task(handler(msg)))
    observe.start()

    while True:
        await asyncio.sleep(1)

async def get_device_by_name():
    """Find and return the Mini robot device."""
    result = await Mini.get_device_by_name("00352", 10)
    print(f"Device Found: {result}")
    return result

async def connection(dev: WiFiDevice) -> bool:
    """Connect to the Mini robot."""
    success = await Mini.connect(dev)
    if success:
        print("Connected to Mini successfully.")
    else:
        print("Failed to connect to Mini.")
    return success

async def start_run_program():
    """Enter program mode."""
    await Mini.enter_program()
    print("Entered program mode.")

async def shutdown():
    """Shutdown and release resources."""
    await Mini.quit_program()
    await Mini.release()
    print("Shutdown completed.")

async def main():
    print("Starting Mini Robot Program...")

    device = await get_device_by_name()
    if not device:
        print("Failed to find Mini robot. Exiting...")
        await shutdown()
        return

    if not await connection(device):
        print("Connection failed. Exiting...")
        await shutdown()
        return

    await start_run_program()
    await test_speech_recognise()  # Runs indefinitely

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except RuntimeError as e:
        print(f"RuntimeError occurred: {e}")
