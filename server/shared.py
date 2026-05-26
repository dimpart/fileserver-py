# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

from typing import Optional, Set, List

from dimples.utils import SysArgvParser
from dimples.utils import Log
from dimples.utils import Singleton
from dimples.utils import Path
from dimples.utils import Config
from dimples.common.compat import LibraryLoader


@Singleton
class GlobalVariable:

    def __init__(self):
        super().__init__()
        self.__config: Optional[Config] = None
        # cached values
        self.__image_types: Optional[Set[str]] = None
        self.__allowed_types: Optional[Set[str]] = None
        self.__allowed_size = None  # default is 16 MB
        self.__secrets: Optional[List[str]] = None
        # load extensions
        LibraryLoader().run()

    @property
    def config(self) -> Config:
        return self.__config

    async def prepare(self, config: Config):
        self.__config = config

    @property
    def server_host(self) -> str:
        return self.config.get_string(section='ftp', option='host')

    @property
    def server_port(self) -> int:
        return self.config.get_integer(section='ftp', option='port')

    #
    #   download
    #

    @property
    def avatar_url(self) -> str:
        return self.config.get_string(section='ftp', option='avatar_url')

    @property
    def download_url(self) -> str:
        return self.config.get_string(section='ftp', option='download_url')

    #
    #   upload
    #

    @property
    def avatar_directory(self) -> str:
        return self.config.get_string(section='ftp', option='avatar_dir')

    @property
    def upload_directory(self) -> str:
        return self.config.get_string(section='ftp', option='upload_dir')

    @property
    def image_file_types(self) -> Set[str]:
        types = self.__image_types
        if types is None:
            types = self.__get_set(section='ftp', option='image_types')
            assert len(types) > 0, 'image file types not set'
            self.__image_types = types
        return types

    @property
    def allowed_file_types(self) -> Set[str]:
        types = self.__allowed_types
        if types is None:
            types = self.__get_set(section='ftp', option='allowed_types')
            assert len(types) > 0, 'allowed file types not set'
            self.__allowed_types = types
        return types

    def __get_set(self, section: str, option: str) -> Set[str]:
        result = set()
        value = self.config.get_string(section=section, option=option)
        assert value is not None, f'string value not found: section={section}, option={option}'
        array = value.split(',')
        for item in array:
            string = item.strip()
            if len(string) > 0:
                result.add(string)
        return result

    def __get_list(self, section: str, option: str) -> List[str]:
        result = []
        value = self.config.get_string(section=section, option=option)
        assert value is not None, f'string value not found: section={section}, option={option}'
        array = value.split(',')
        for item in array:
            string = item.strip()
            if len(string) > 0:
                result.append(string)
        return result

    @property
    def allowed_file_size(self) -> int:
        size = self.__allowed_size
        if size is None:
            size = self.config.get_integer(section='ftp', option='allowed_size')
            if size <= 0:
                size = 1 << 24  # 16 MB
            self.__allowed_size = size
        return size

    @property
    def md5_secrets(self) -> List[str]:
        secrets = self.__secrets
        if secrets is None:
            secrets = self.__get_list(section='ftp', option='md5_secrets')
            assert len(secrets) > 0, 'md5 keys not set'
            self.__secrets = secrets
        return secrets


async def create_config(sys_argv: SysArgvParser, default_config: str) -> Optional[Config]:
    """ Step 1: load config """
    #
    #  get INI file
    #
    ini_file = sys_argv.get_opt(opt='config')
    if ini_file is None:
        ini_file = default_config
    if not await Path.exists(path=ini_file):
        Log.error('!!! config file not exists: %s', ini_file)
        return None
    shared = GlobalVariable()
    #
    #  load config
    #
    config = Config()
    await config.load(path=ini_file)
    Log.warning('>>> config loaded: %s => %s', ini_file, config)
    await shared.prepare(config=config)
    return config
