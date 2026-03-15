# Face Detection
'''
Important Libraries

'''
import logging
import asyncio

import mini.mini_sdk as Mini
from mini.dns.dns_browser import WiFiDevice
'''
Important Libraries

'''

'''
AlphaMini Libraries for TTS

'''

from mini.apis import errors
from mini.apis.api_sound import StartPlayTTS, StopPlayTTS, ControlTTSResponse
from mini.apis.api_sound import StopAllAudio, StopAudioResponse
from mini.apis.base_api import MiniApiResultType

'''
AlphaMini Libraries for Face Detect

'''
from mini.apis.api_observe import ObserveFaceDetect
from mini.apis.api_sound import StartPlayTTS

from mini.pb2.codemao_facedetecttask_pb2 import FaceDetectTaskResponse
#from test.test_connect import test_connect, shutdown
#clearfrom test.test_connect import test_get_device_by_name, test_start_run_program


#logging information 
Mini.set_log_level(logging.INFO)
Mini.set_log_level(logging.DEBUG)
Mini.set_robot_type(Mini.RobotType.EDU) #AlphaMini Overseased, declaration -> Important


#Function for Text to Speech.
async def _play_tts():
    block: StartPlayTTS = StartPlayTTS(text="Hello! We are  R A I Students, In PSB Academy") #Edit the " " for different speech.
    (resultType, response) = await block.execute()
    print(f'{response}')
    return()


#Function for Face Detect
async def test_ObserveFaceDetect():
    """人脸个数检测demo

    人脸个数检测,检测到人脸,则上报事件

    当检测到人脸个数大于等于1个时，停止监听，并播报"在我面前好像有xx个人脸"(xx为人脸个数)

    """
    observer: ObserveFaceDetect = ObserveFaceDetect()

    # FaceDetectTaskResponse.count
    # FaceDetectTaskResponse.isSuccess
    # FaceDetectTaskResponse.resultCode
    def handler(msg: FaceDetectTaskResponse):
        print(f"{msg}")
        if msg.isSuccess and msg.count:
            observer.stop()
            asyncio.create_task(_play_tts2(msg.count))

    observer.set_handler(handler)
    observer.start()
    await asyncio.sleep(0)


async def _play_tts2(count: int):
    await StartPlayTTS(text=f'There are {count} people in front of me').execute()
   #asyncio.get_running_loop().run_in_executor(None, asyncio.get_running_loop().stop)

'''

Connection Initialization Code (Computer to AlphaMini).

'''

#Function for Finding Device -> Important 
async def get_device_by_name():
    result: WiFiDevice = await Mini.get_device_by_name("00352", 10)  #Please enter AlphaMini-Robot ID  "00352"
    print(f"test_get_device_by_name result:{result}")
    return result

#Function for Binding Device with Computer-> Important 
async def connection(dev: WiFiDevice) -> bool:
    return await Mini.connect(dev)



#Function for starting a main Progarm loop -> Important
async def start_run_program():
    await Mini.enter_program()


#Function for Shutdown Progarm -> Important
async def shutdown():
    await Mini.quit_program()
    await Mini.release()

'''

Connection Initialization Code (Computer to AlphaMini).

'''


#Main Function
async def main():
    device: WiFiDevice = await get_device_by_name()
    if device:
        await connection(device)
        await start_run_program()
        await _play_tts()
        await test_ObserveFaceDetect()
        
        await asyncio.sleep(10)  # Give enough time for all TTS and detections to complete
        
        await shutdown()

if __name__ == '__main__' :
    asyncio.run(main())
