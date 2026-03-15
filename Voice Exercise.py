import asyncio
import logging
import mini.mini_sdk as Mini

from mini.apis.api_observe import ObserveSpeechRecognise
from mini.apis.api_sound import StartPlayTTS
from mini.apis.api_action import MoveRobot, MoveRobotDirection, MoveRobotResponse
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.base_api import MiniApiResultType
from mini.dns.dns_browser import WiFiDevice
from mini.pb2.codemao_speechrecognise_pb2 import SpeechRecogniseResponse

# Set logging level for debugging
Mini.set_log_level(logging.DEBUG)
Mini.set_robot_type(Mini.RobotType.EDU)

async def play_tts(text: str):
    """Plays text using Text-to-Speech (TTS)."""
    block = StartPlayTTS(text=text)
    await block.execute()

async def move_forward():
    """Moves the robot forward."""
    block = MoveRobot(step=6, direction=MoveRobotDirection.FORWARD)
    resultType, response = await block.execute()

    if resultType == MiniApiResultType.Success and response.isSuccess:
        print("Robot is walking forward.")
    else:
        print("Failed to move forward.")
        
async def test_play_action():
    block: PlayAction = PlayAction(action_name='014')
    (resultType, response) = await block.execute()
    print(f'test_play_action result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_play_action timeout'
    assert response is not None and isinstance(response, PlayActionResponse), 'test_play_action result unavailable'
    assert response.isSuccess, 'play_action failed'

async def speech_recognition():
    """Listens for voice commands and responds."""
    observe = ObserveSpeechRecognise()

    async def handler(msg: SpeechRecogniseResponse):
        recognized_text = str(msg.text).strip().lower()
        print(f'Recognized: "{recognized_text}"')

        if recognized_text == "hello.":
            await play_tts("Hello, I am AlphaMini! How can I assist?")
        elif recognized_text == "exercise.":
            await play_tts("Alright, I am walking now!")
            await move_forward()
        elif recognized_text == "kung fu.":
            await play_tts("Alright, I am showing now!")
            await test_play_action()
        elif recognized_text == "stop here.":
            await play_tts("Stopping voice recognition.")

    observe.set_handler(lambda msg: asyncio.create_task(handler(msg)))
    observe.start()

    while True:
        await asyncio.sleep(1)

async def get_device():
    """Find and return the Mini robot device."""
    return await Mini.get_device_by_name("00352", 10)

async def connect_to_robot(device: WiFiDevice):
    """Connect to AlphaMini."""
    return await Mini.connect(device)

async def shutdown():
    """Shutdown and release resources."""
    await Mini.quit_program()
    await Mini.release()
    print("Shutdown complete.")

async def main():
    """Main execution."""
    device = await get_device()
    if not device:
        print("Mini robot not found!")
        await shutdown()
        return

    if not await connect_to_robot(device):
        print("Connection failed.")
        await shutdown()
        return

    await Mini.enter_program()
    await speech_recognition()  # Keep listening for commands

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"Error: {e}")
