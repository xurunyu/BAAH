from nicegui import ui, run
from modules.utils import connect_to_device, get_now_running_app,  get_now_running_app_entrance_activity, screen_shot_to_global, screencut_tool

def screencut_button(inconfig, resultdict, resultkey, input_text="Screencut", button_text="Screencut"):
    """
    截图，截图文件名，截图按钮
    """
    with ui.row():
        # 图片
        ui.image(resultdict[resultkey]).bind_source_from(resultdict, resultkey).style("width: 400px")
    
    with ui.row():
        ui.input(input_text).bind_value(resultdict, resultkey).style("width: 400px")
        ui.button(button_text, on_click=lambda: cut_screenshot(inconfig=inconfig, resultdict=resultdict, resultkey=resultkey, left_click=True, right_click=False, quick_return=True))
    

cut_lock = False
async def cut_screenshot(inconfig, resultdict=None, resultkey=None, left_click=True, right_click=False, quick_return=True):
    """
    截取截图的一部分，返回截图文件名
    """
    
    global cut_lock
    if cut_lock:
        print("Multiple cut_screenshot is not allowed")
        return
    cut_lock = True
    result = None
    try:
        connect_to_device(use_config=inconfig)
        screen_shot_to_global(use_config=inconfig, output_png=True)
        screenshotname = inconfig.userconfigdict['SCREENSHOT_NAME']
        result = await run.io_bound(
            screencut_tool,
            left_click=left_click,
            right_click=right_click,
            img_path=screenshotname,
            quick_return=quick_return
        )
        if resultdict is not None and resultkey is not None:
            resultdict[resultkey] = result
    except Exception as e:
        print(e.__traceback__)
    finally:
        cut_lock = False
    return result