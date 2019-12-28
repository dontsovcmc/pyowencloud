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

        parameters_id = [p['id'] for p in device_info['parameters']]


        # parameters_id = [123456]
        params_info = cloud.last_data(parameters_id)
        # Печатаем последние значения параметров устройства
        #pprint(params_info)

        for param_info in params_info:
            value_info = param_info['values'][0]
            dt = datetime.utcfromtimestamp(value_info['d'])

            if not value_info['e']:
                # 123456: 41.6 (2019-12-28 11:25:41)
                print('{}: {} ({})'.format(param_info['id'],
                                           float(value_info['v']),
                                           dt.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                # 123456: ERROR 1
                print('{}: ERROR {}'.format(param_info['id'],
                                            param_info['e']))
