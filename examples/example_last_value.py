# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import time
from pyowencloud import OwenClient, OwenException, NoDataException


if __name__ == "__main__":
    """
    """
    user, password = sys.argv[1].split(':')

    while True:
        try:
            cloud = OwenClient()

            cloud.login(user, password)

            termometer = cloud.devices(u'термометр')[0]

            temperature_id = cloud.parameters(termometer['id'], u'Температура')[0]

            last_timestamp = 0
            while True:
                try:
                    value, last_timestamp = cloud.last_value_with_dt(temperature_id, last_timestamp)
                    print(value)
                except OwenException as err:
                    print('Ошибка: {}'.format(err))
                except NoDataException:
                    print('Нет новых данных')
                time.sleep(10)

        finally:
            cloud.disconnect()
