from ..components.exec_arg_parse import get_token
from ..components.manage_baah_in_gui import run_baah_task_and_bind_log, stop_baah_task
from ..components.running_task_pool import RunningBAAHProcess_instance
from ..pages.Setting_BAAH import set_BAAH
from ..pages.Setting_Craft import set_craft
from ..pages.Setting_cafe import set_cafe
from ..pages.Setting_emulator import set_emulator
from ..pages.Setting_event import set_event
from ..pages.Setting_exchange import set_exchange
from ..pages.Setting_hard import set_hard
from ..pages.Setting_normal import set_normal
from ..pages.Setting_other import set_other
from ..pages.Setting_server import set_server
from ..pages.Setting_shop import set_shop
from ..pages.Setting_special import set_special
from ..pages.Setting_task_order import set_task_order # 此方法内有个导入myAllTask，可能导致下述异常
from ..pages.Setting_timetable import set_timetable
from ..pages.Setting_wanted import set_wanted
from ..pages.Setting_notification import set_notification
from ..pages.Setting_vpn import set_vpn
from ..pages.Setting_Assault import set_assault
from ..pages.Setting_BuyAP import set_buyAP
from ..pages.Setting_UserTask import set_usertask
from modules.AllTask.myAllTask import task_instances_map # 这里导入myAllTask可能会导致其内my_AllTask单例值异常，目前通过在run()里使用前再读取config的任务列表解决此bug
from modules.configs.MyConfig import MyConfigger
from ..define import gui_shared_config, injectJSforTabs

from nicegui import ui, app, run
from typing import Callable
import os
import time


class ConfigPanel:
    """
    连接子页面的i18n名称 与 渲染页面的函数

    Parameters
    ==========
    nameID: str
        子页面标题的i18n的key 或 标题名
    func: 
        子页面渲染函数
    lst_config: Config
        传入时通过nameID找到对应i18n名字，为None时name=nameID
    """
    def __init__(self, nameID: str, func: Callable[[], None], lst_config=None):
        self.name = lst_config.get_text(nameID) if lst_config else nameID
        self.func = func
        self.tab = None
        self.nameID = nameID

    def set_tab(self, tab: ui.tab):
        self.tab = tab


def get_config_list(lst_config: MyConfigger) -> list:
    return [
        ConfigPanel("BAAH", lambda: set_BAAH(lst_config, gui_shared_config), lst_config=None),
        ConfigPanel("setting_emulator", lambda: set_emulator(lst_config), lst_config=lst_config),
        ConfigPanel("setting_server", lambda: set_server(lst_config), lst_config=lst_config),
        ConfigPanel("setting_vpn", lambda: set_vpn(lst_config), lst_config=lst_config),
        ConfigPanel("setting_task_order", lambda: set_task_order(lst_config, task_instances_map.task_config_name_2_i18n_name), lst_config=lst_config),
        ConfigPanel("setting_notification", lambda: set_notification(lst_config, gui_shared_config), lst_config=lst_config),
        ConfigPanel("task_cafe", lambda: set_cafe(lst_config), lst_config=lst_config),
        ConfigPanel("task_timetable", lambda: set_timetable(lst_config), lst_config=lst_config),
        ConfigPanel("task_craft", lambda: set_craft(lst_config), lst_config=lst_config),
        ConfigPanel("task_shop", lambda: set_shop(lst_config), lst_config=lst_config),
        ConfigPanel("task_buy_ap", lambda: set_buyAP(lst_config), lst_config=lst_config),
        ConfigPanel("task_wanted", lambda: set_wanted(lst_config), lst_config=lst_config),
        ConfigPanel("task_special", lambda: set_special(lst_config), lst_config=lst_config),
        ConfigPanel("task_exchange", lambda: set_exchange(lst_config), lst_config=lst_config),
        ConfigPanel("task_event", lambda: set_event(lst_config), lst_config=lst_config),
        ConfigPanel("task_assault", lambda: set_assault(lst_config), lst_config=lst_config),
        ConfigPanel("task_hard", lambda: set_hard(lst_config, gui_shared_config), lst_config=lst_config),
        ConfigPanel("task_normal", lambda: set_normal(lst_config), lst_config=lst_config),
        ConfigPanel("task_user_def_task", lambda: set_usertask(lst_config), lst_config=lst_config),
        ConfigPanel("setting_other", lambda: set_other(lst_config, lst_config.nowuserconfigname), lst_config=lst_config)
    ]


@ui.page('/panel/{json_file_name}')
def show_json_panel(json_file_name: str):
    if get_token() is not None and get_token() != app.storage.user.get("token"):
        return
    curr_config: MyConfigger = MyConfigger()
    curr_config.parse_user_config(json_file_name)
    config_choose_list: list[ConfigPanel] = get_config_list(curr_config)

    # 设置splitter高度使其占满全屏，减去2rem是content这个class的内边距
    with ui.splitter(value=15).classes('w-full h-full').style("height: calc(100vh - 2rem);") as splitter:
        with splitter.before:
            ui.button("<-", on_click=lambda: ui.run_javascript('window.history.back()'))
            # 便于js查找tabs
            with ui.tabs().props('vertical').classes('w-full loctabs') as tabs:
                for i, config_cls in enumerate(config_choose_list):
                    config_choose_list[i].set_tab(ui.tab(config_cls.name))

        with splitter.after:
            # 便于js查找被滚动元素
            with ui.tab_panels(tabs, value=config_choose_list[0].tab).props('vertical').classes('w-full h-full locscroll'):
                for cls in config_choose_list:
                    with ui.tab_panel(cls.tab):
                        ui.html("<div style='width: 1px;height: 20px'></div>")
                        cls.func()
                        ui.html("<div style='width: 1px;height: 200px'></div>")

        ui.add_head_html(injectJSforTabs)

        with ui.column().style('flex-grow: 1;width: 30vw;position:sticky; top: 0px;'):
            output_card = ui.card().style('width: 30vw; height: 80vh;overflow-y: auto;')
            with output_card:
                logArea = ui.log(max_lines=1000).classes('w-full h-full')

        with ui.column().style(
                'width: 10vw; overflow: auto; position: fixed; bottom: 40px; right: 20px;min-width: 150px;'):
            def save_and_alert():
                curr_config.save_user_config(json_file_name)
                curr_config.save_software_config()
                gui_shared_config.save_software_config()
                ui.notify(curr_config.get_text("notice_save_success"))

            ui.button(curr_config.get_text("button_save"), on_click=save_and_alert)

            def save_and_alert_and_run_in_terminal():
                curr_config.save_user_config(json_file_name)
                curr_config.save_software_config()
                gui_shared_config.save_software_config()
                ui.notify(curr_config.get_text("notice_save_success"))
                ui.notify(curr_config.get_text("notice_start_run"))
                # 打开同目录中的BAAH.exe，传入当前config的json文件名
                os.system(f'start BAAH.exe "{json_file_name}"')

            ui.button(curr_config.get_text("button_save_and_run_terminal"), on_click=save_and_alert_and_run_in_terminal)

            # ======Run in GUI======
            async def save_and_alert_and_run():
                curr_config.save_user_config(json_file_name)
                curr_config.save_software_config()
                gui_shared_config.save_software_config()
                ui.notify(curr_config.get_text("notice_save_success"))
                ui.notify(curr_config.get_text("notice_start_run"))
                await run.io_bound(run_baah_task_and_bind_log, logArea, json_file_name)

            # log recovery
            msg_obj = RunningBAAHProcess_instance.get_status_obj(configname=json_file_name)
            print(f"This config's ({json_file_name}) msg obj is {msg_obj}")
            # 如果此config相关任务正在运行，使用save_and_alert_and_run绑定日志输出到GUI日志窗口内
            if msg_obj["runing_signal"] == 1:
                track_logger_timer = ui.timer(0.5, save_and_alert_and_run, once=True)

            ui.button(curr_config.get_text("button_save_and_run_gui"), on_click=save_and_alert_and_run).bind_visibility_from(
                msg_obj, "runing_signal", backward=lambda x: x == 0)

            async def stop_run() -> None:
                stop_baah_task(logArea, json_file_name)

            ui.button(curr_config.get_text("notice_finish_run"), on_click=stop_run, color='red').bind_visibility_from(
                msg_obj, "runing_signal", backward=lambda x: x == 1)

            ui.button("...").bind_visibility_from(msg_obj, "runing_signal", backward=lambda x: x == 0.25)

            # ================


    # 加载完毕保存一下config，应用最新的对config的更改
    curr_config.save_user_config(json_file_name)
    curr_config.save_software_config()
