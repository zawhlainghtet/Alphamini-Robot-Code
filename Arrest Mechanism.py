# Arrest Mechanism
import asyncio
import logging

from mini import mini_sdk as MiniSdk
from mini.apis.api_action import GetActionList, GetActionListResponse, RobotActionType
from mini.apis.api_action import MoveRobot, MoveRobotDirection, MoveRobotResponse
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.base_api import MiniApiResultType
from mini.dns.dns_browser import WiFiDevice
#from test.test_connect import test_get_device_by_name


MiniSdk.set_robot_type(MiniSdk.RobotType.EDU) #AlphaMini Overseased, declaration -> Important
MiniSdk.set_log_level(logging.INFO)
MiniSdk.set_log_level(logging.DEBUG)

# 测试, 执行一个动作文件
async def test_play_action():
   
    # action_name: 动作文件名, 可以通过GetActionList获取机器人支持的动作
    block: PlayAction = PlayAction(action_name='Surveillance_003')
    # response: PlayActionResponse
    (resultType, response) = await block.execute()

    print(f'test_play_action result:{response}')

    assert resultType == MiniApiResultType.Success, 'test_play_action timetout'
    assert response is not None and isinstance(response, PlayActionResponse), 'test_play_action result unavailable'
    assert response.isSuccess, 'play_action failed'



async def test_move_robot():
    block: MoveRobot = MoveRobot(step=3,direction=MoveRobotDirection.FORWARD)
    (resultType, response) = await block.execute()
    print(f'test_move_robot result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_move_robot timetout'
    assert response is not None and isinstance(response, MoveRobotResponse), 'test_move_robot result unavailable'
    assert response.isSuccess, 'move_robot failed'





async def get_device_by_name():
    result: WiFiDevice = await MiniSdk.get_device_by_name("00352", 10)  #Please enter AlphaMini-Robot ID  "00352"
    print(f"test_get_device_by_name result:{result}")
    return result


async def main():
    device: WiFiDevice = await get_device_by_name()
    if device:
        await MiniSdk.connect(device)
        await MiniSdk.enter_program()
        await test_play_action()
    #   await test_move_robot()
        await test_get_action_list()
        await MiniSdk.quit_program()
        await MiniSdk.release()


if __name__ == '__main__':
    asyncio.run(main())
