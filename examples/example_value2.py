# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
from pyowencloud import OwenClient, OwenException, NoDataException

if __name__ == "__main__":
    """
    """
    user, password = sys.argv[1].split(':')
    cloud = OwenClient()

    cloud.login(user, password)

    termometer = cloud.devices(u'термометр')[0]

    temperature_id = cloud.parameters(termometer['id'], u'Температура')[0]

    last_timestamp = 0
    try:
        value_info = cloud.last_value(temperature_id, last_timestamp)
    except OwenException as err:
        print('Ошибка: {}'.format(err))
    except NoDataException:
        print('Нет новых данных')
