import logging
import asyncio
import time
import mini.mini_sdk as Mini
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_sound import StartPlayTTS
from mini.apis.api_observe import ObserveFaceRecognise
from mini.apis.base_api import MiniApiResultType

# Set logging level
Mini.set_log_level(logging.DEBUG)

# Set Robot Type (Important)
Mini.set_robot_type(Mini.RobotType.EDU)  # Ensure this matches your robot type

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
                asyncio.create_task(__tts(detected_name))
    
    observer.set_handler(handler)
    observer.start()

    # Keep it running to allow recognition
    while True:
        await asyncio.sleep(1)

# Function for Text-to-Speech
async def __tts(name):
    print(f"Speaking: Hello，{name},Your attendance is marked.")
    await StartPlayTTS(text=f'Hello， {name}... your attendance has been marked and stored.. Welcome to Singapore Police Academy').execute()

# Function for Finding Device
async def get_device_by_name():
    result = await Mini.get_device_by_name("00352", 10)  # Change ID if needed
    print(f"Device Search Result: {result}")
    return result

# Function for Connecting to Robot
async def connection(dev: WiFiDevice) -> bool:
    return await Mini.connect(dev)

# Function for starting program loop
async def start_run_program():
    await Mini.enter_program()

# Function for Shutdown
async def shutdown():
    await Mini.quit_program()
    await Mini.release()

# Main Function
async def main():
    device = await get_device_by_name()

    if device:
        if await connection(device):
            print("Connected to Robot!")

            task = asyncio.create_task(FaceRecognition())
            await asyncio.sleep(30)

            task.cancel()
            await shutdown()
        else:
            print("Failed to connect to robot.")

# Run the program
if __name__ == '__main__':
    asyncio.run(main())
