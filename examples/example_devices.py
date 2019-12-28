# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
from pprint import pprint
from pyowencloud import OwenClient

if __name__ == "__main__":
    """
    """
    user, password = sys.argv[1].split(':')
    cloud = OwenClient()

    # Логинимся, токен сохраняется в cloud
    cloud.login(user, password)

    devices = cloud.devices()

    # Печатаем список устройств пользователя
    pprint(devices)
