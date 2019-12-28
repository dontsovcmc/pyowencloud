# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
from pprint import pprint
from datetime import datetime

from pyowencloud import OwenClient


if __name__ == "__main__":
    """
    """
    user, password = sys.argv[1].split(':')
    cloud = OwenClient()

    # Логинимся, токен сохраняется в cloud
    cloud.login(user, password)

    devices = cloud.devices()

    devices_ids = [d['id'] for d in devices]
    for id in devices_ids:
        device_info = cloud.device(id)

        # Печатаем данные по устройству
        pprint(device_info)

        parameters_id = [p['id'] for p in device_info['parameters']]

        params_info = cloud.last_data(parameters_id)
        # Печатаем последние значения параметров устройства
        pprint(params_info)
