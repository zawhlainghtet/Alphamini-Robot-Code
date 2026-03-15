import logging
import asyncio
import time
import mini.mini_sdk as MiniSdk
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_sound import StartPlayTTS
from mini.apis.api_observe import ObserveFaceRecognise
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.api_action import MoveRobot, MoveRobotDirection, MoveRobotResponse
from mini.apis.base_api import MiniApiResultType

# Set logging level
MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)  # Ensure correct robot type
MiniSdk.set_log_level(logging.DEBUG)

last_recognized_face = None
last_detection_time = 5
Detection_delay = 10

# Function to handle Face Recognition
async def FaceRecognition():
    observer = ObserveFaceRecognise()

    # Handler function for face recognition
    def handler(msg):
        global last_recognized_face, last_detection_time

        if msg.isSuccess and msg.faceInfos:
            detected_name = msg.faceInfos[0].name
            current_time = time.time()
            if detected_name != last_recognized_face or (current_time - last_detection_time > Detection_delay):
                last_recognized_face = detected_name
                last_detection_time = current_time
                print(f"Detected Face: {detected_name}")
                
                # Trigger TTS
                asyncio.create_task(__tts(detected_name))
                
                # Execute Arrest Mechanism
                asyncio.create_task(test_move_robot())
                
                asyncio.create_task(execute_arrest())

    observer.set_handler(handler)
    observer.start()

    # Keep it running to allow recognition
    while True:
        await asyncio.sleep(1)

# Function for Text-to-Speech
async def __tts(name):
    
    print(f"Speaking: Hey, {name}, you are robber.recorded.")
    await StartPlayTTS(text=f'Hey, {name}, you are robber. Stay there, do not move.').execute()
    
    
async def test_move_robot():
    block: MoveRobot = MoveRobot(step=1, direction=MoveRobotDirection.BACKWARD)
    (resultType, response) = await block.execute()
    print(f'test_move_robot result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_move_robot timetout'
    assert response is not None and isinstance(response, MoveRobotResponse), 'test_move_robot result unavailable'
    assert response.isSuccess, 'move_robot failed'

# Function to execute Arrest Mechanism
async def execute_arrest():
    print("Executing Arrest Mechanism...")
    await asyncio.sleep(4)
    # Step 1: Play Surveillance Action
    action_result = await PlayAction(action_name='Surveillance_003').execute()
    if action_result[0] == MiniApiResultType.Success and action_result[1].isSuccess:
        print("Action 'Surveillance_003' executed successfully.")
    else:
        print("Failed to execute 'Surveillance_003'.")


# Function to get device by name
async def get_device_by_name():
    result = await MiniSdk.get_device_by_name("00352", 10)  # Change ID if needed
    print(f"Device Search Result: {result}")
    return result

# Function for Connecting to Robot
async def connection(dev: WiFiDevice) -> bool:
    return await MiniSdk.connect(dev)

# Function for Shutdown
async def shutdown():
    await MiniSdk.quit_program()
    await MiniSdk.release()

# Main Function
async def main():
    device = await get_device_by_name()

    if device:
        if await connection(device):
            print("Connected to Robot!")

            task = asyncio.create_task(FaceRecognition())
            await asyncio.sleep(60)

            task.cancel()
            await shutdown()
        else:
            print("Failed to connect to robot.")

# Run the program
if __name__ == '__main__':
    asyncio.run(main())
