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

    cloud.login(user, password)

    termometer = cloud.devices(u'термометр')[0]

    temperature_id = cloud.parameters(termometer['id'], u'Температура')[0]

    value_info = cloud.last_value_info(temperature_id)

    # Печатаем последние значения параметров устройства
    #pprint(value_info)

    if not value_info['e']:
        # 123456: 41.6 (2019-12-28 11:25:41)
        print('{}: {} ({})'.format(temperature_id,
                                   float(value_info['v']),
                                   datetime.utcfromtimestamp(value_info['d']).strftime('%Y-%m-%d %H:%M:%S UTC')))
    else:
        # 123456: ERROR 1
        print('{}: ERROR {}'.format(temperature_id,
                                    value_info['e']))
