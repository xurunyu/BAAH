import json
import os
import time
from modules.configs.defaultSettings import defaultUserDict, defaultSoftwareDict, defaultSessionDict
from modules.configs.settingMaps import configname2screenshotname
# 程序入口先import这个实例，然后调用parse_user_config方法解析该config实例
# 然后在其他模块中import这个实例，就可以直接使用这个类的实例了，所有使用（变量的获取/设置）应当放在运行时而不是导入时

# TODO: 介于以上问题，此种模式的单例在依赖同单例模式的config时会在使用时出现bug：比如 如果此方法的单例m（myAllTask）是在初始化时读取config值并存储。一段代码先导入实例m，随后对config实例做出parse，再使用实例m，此时实例m存储的依旧是config修改前的值

class MyConfigger:
    """
    维护config字典，包含软件config，用户任务config，语言包
    """
    NOWVERSION="1.8.2"
    USER_CONFIG_FOLDER="./BAAH_CONFIGS"
    SOFTWARE_CONFIG_FOLDER="./DATA/CONFIGS"
    LANGUAGE_PACKAGE_FOLDER="./DATA/i18n"
    SOFTWARE_CONFIG_NAME="software_config.json"
    # 读取config这个py里面的配置
    def __init__(self):
        self.current_dir = os.getcwd()
        # 软件的config
        self.softwareconfigdict = {}
        # 软件的语言包
        self.languagepackagedict = {}
        # 一次区服任务的config
        self.userconfigdict = {}
        self.nowuserconfigname = ""
        # 一次区服任务运行的session
        self.sessiondict = {}
        self._check_session_config()
        # 读取软件的config
        self.parse_software_config(self.SOFTWARE_CONFIG_NAME)

    def parse_user_config(self, file_name, clear_sessiondict = True):
        """
        读取config文件并解析
        同时会按需清空sessiondict
        """
        file_path = os.path.join(self.current_dir, self.USER_CONFIG_FOLDER, file_name)
        # 字典新值
        self.userconfigdict = self._read_config_file(file_path)
        if clear_sessiondict:
            # 清空sessiondict
            self.sessiondict = {}
            self._check_session_config()
        # 检查缺失的配置
        self._check_user_config()
        self.nowuserconfigname = file_name
        # 强制设置截图文件名为配置名
        self.userconfigdict["SCREENSHOT_NAME"] = configname2screenshotname(file_name)
        # 检查截图文件夹路径里是否有DATA, 如果没有DATA，说明是1.1.x版本的配置，需要转换
        if "DATA" not in self.userconfigdict["PIC_PATH"]:
            fromkey = defaultUserDict["PIC_PATH"]["m"]["from"]
            mapfunc = defaultUserDict["PIC_PATH"]["m"]["map"]
            self.userconfigdict["PIC_PATH"] = mapfunc(self.userconfigdict[fromkey])
        # 输出
        # print("user config字典内容: "+ ",".join([k for k in self.userconfigdict]))
    
    def parse_software_config(self, file_name):
        """
        读取config文件并解析，
        同时加载语言包
        """
        file_path = os.path.join(self.current_dir, self.SOFTWARE_CONFIG_FOLDER, file_name)
        # 字典新值
        self.softwareconfigdict = self._read_config_file(file_path)
        # 检查缺失的配置
        self._check_software_config()
        # 强制设定VERSION
        self.softwareconfigdict["NOWVERSION"] = self.NOWVERSION
        # 输出
        # print("software config字典内容: "+ ",".join([k for k in self.softwareconfigdict]))
        # 加载语言包
        self.parse_language_package(self.softwareconfigdict["LANGUAGE"]+".json")
    
    def parse_language_package(self, file_name):
        """
        读取语言包文件并解析
        """
        file_path = os.path.join(self.current_dir, self.LANGUAGE_PACKAGE_FOLDER, file_name)
        # 字典新值
        self.languagepackagedict = self._read_config_file(file_path)
        # print("language package字典内容: "+ ",".join([k for k in self.languagepackagedict]))
        
    @staticmethod
    def get_all_user_config_names()->list[str]:
        """
        获取所有用户配置文件名
        """
        user_config_folder = os.path.join(os.getcwd(), MyConfigger.USER_CONFIG_FOLDER)
        whetherHasFolder = os.path.exists(user_config_folder)
        if not whetherHasFolder:
            return []
        return [f for f in os.listdir(user_config_folder) if f.endswith(".json")]

    def _read_config_file(self, file_path):
        """
        读取文件，返回字典
        """
        try:
            if os.path.getsize(file_path) == 0:
                raise FileNotFoundError(f"No Such File: {file_path}")
            with open(file_path, 'r', encoding="utf8") as f:
                dictconfig = json.load(f)
                # print("读取{}文件成功, 读取了{}个配置".format(file_path, len(dictconfig)))
                return dictconfig
        except FileNotFoundError as e:
            # 检查文件名
            [path, filename] = os.path.split(file_path)
            # 以json结尾的文件，如果不存在，此处返回空字典
            # 自动填写好默认值后，让用户自己选择是否保存
            if filename.endswith(".json"):
                # print(f'文件不存在： {file_path}, 以默认值创建')
                # os.makedirs(path, exist_ok=True)
                # with open(file_path, 'w', encoding="utf8") as f:
                #     json.dump({}, f, indent=4, ensure_ascii=False)
                print(f'试图读取的配置文件 {file_path} 不存在，这里使用预设的默认值代替')
                print(f'no such file: {file_path}, use default value instead')
                return {}
            else:
                raise Exception(f'文件不存在： {file_path}')
        except Exception as e:
            raise Exception(f'读取{file_path}文件时发生错误，请检查{file_path}文件: {str(e)}')

    def _fill_by_map_or_default(self, defaultmap, selfmap, key, print_warn = True):
        """
        尝试用defaultmap里的map和default值填充某个key
        """
        # 使用对应关系查找
        if "m" in defaultmap[key]:
            mapdict = defaultmap[key]["m"]
            fromkey = mapdict["from"]
            mapfunc = mapdict["map"]
            if fromkey in selfmap:
                # 能用对应关系就用对应关系
                selfmap[key] = mapfunc(selfmap[fromkey])
                if print_warn:
                    print("缺少{}配置，根据{}配置自动填充为{}".format(key, fromkey, selfmap[key]))
            else:
                # 对应关系的键不在，那就只能用默认值
                if print_warn:
                    print("缺少{}配置，使用默认值{}".format(key, defaultmap[key]["d"]))
                selfmap[key] = defaultmap[key]["d"]
        else:
            # 没有对应关系就只能默认值
            if print_warn:
                print("缺少{}配置，使用默认值{}".format(key, defaultmap[key]["d"]))
            selfmap[key] = defaultmap[key]["d"]

    def _check_user_config(self):
        """
        检查用户的config内的值是否有缺少，如果有，按照对应关系查找，如果没有，就用默认值
        """
        # 先处理SERVER_TYPE
        if "SERVER_TYPE" not in self.userconfigdict:
            # 使用对应关系查找
            mapdict = defaultUserDict["SERVER_TYPE"]["m"]
            fromkey = mapdict["from"]
            mapfunc = mapdict["map"]
            if fromkey in self.userconfigdict:
                self.userconfigdict["SERVER_TYPE"] = mapfunc(self.userconfigdict[fromkey])
            else:
                self.userconfigdict["SERVER_TYPE"] = defaultUserDict["SERVER_TYPE"]["d"]
        for shouldKey in defaultUserDict:
            # 如果用户的config里没有这个值
            if shouldKey not in self.userconfigdict:
                self._fill_by_map_or_default(defaultUserDict, self.userconfigdict, shouldKey)

    def _check_software_config(self):
        """
        检查软件的config内的值是否有缺少，如果有，按照对应关系查找，如果没有，就用默认值
        """
        for shouldKey in defaultSoftwareDict:
            # 如果用户的config里没有这个值
            if shouldKey not in self.softwareconfigdict:
                self._fill_by_map_or_default(defaultSoftwareDict, self.softwareconfigdict, shouldKey)
    
    def _check_session_config(self):
        """
        session内的值设置默认值，sessiondict的值会在运行时被修改
        """
        for shouldKey in defaultSessionDict:
            # 如果没有这个值
            if shouldKey not in self.sessiondict:
                self._fill_by_map_or_default(defaultSessionDict, self.sessiondict, shouldKey, print_warn=False)

    def get_text(self, text_id):
        """
        获取语言包对应id的字符串
        """
        return self.languagepackagedict.get(text_id, f"%{text_id}%")
    
    def save_user_config(self, file_name):
        file_path = os.path.join(self.current_dir, self.USER_CONFIG_FOLDER, file_name)
        with open(file_path, 'w', encoding="utf8") as f:
            json.dump(self.userconfigdict, f, indent=4, ensure_ascii=False)
    
    def save_software_config(self):
        file_path = os.path.join(self.current_dir, self.SOFTWARE_CONFIG_FOLDER, self.SOFTWARE_CONFIG_NAME)
        with open(file_path, 'w', encoding="utf8") as f:
            json.dump(self.softwareconfigdict, f, indent=4, ensure_ascii=False)
    
    def get_one_version_num(self, versionstr=None):
        """
        将版本号字符串转换成数字
        
        如 1.4.10 -> 10410
        """

        try:
            if not versionstr:
                versionstr = self.NOWVERSION
            versionlist = versionstr.split(".")
            return int(versionlist[0])*10000+int(versionlist[1])*100+int(versionlist[2])
        except Exception as e:
            print(e)
            return -1

    def get_version_str(self, versionnum=None):
        """
        将版本号数字转换成字符串
        """
        if versionnum is None:
            return self.NOWVERSION
        try:
            assert isinstance(versionnum, int)
            assert versionnum > 0
            return f"{int(versionnum/10000)}.{int(versionnum%10000/100)}.{versionnum%100}"
        except Exception as e:
            print(e)
            return "0.0.0"



config=MyConfigger()
"""
单例，导入后使用parse_user_config方法解析某个config
"""