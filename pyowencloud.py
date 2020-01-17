# -*- coding: utf-8 -*-
from __future__ import print_function

from requests import Session
from requests.exceptions import HTTPError
from datetime import datetime


class OwenException(Exception):
    pass


class NoDataException(Exception):
    pass


def dt(timestamp):
    if isinstance(timestamp, datetime):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


class OwenClient:
    """
    Python клиент к https://api.owencloud.ru
    """

    def __init__(self):
        self.session = Session()
        self.root = 'https://api.owencloud.ru'
        self.headers = {'Content-Type': 'application/json'}
        self.token = ''

    def disconnect(self):
        try:
            self.session.close()
        except Exception:
            pass

    def assert_error(self, ret):
        try:
            ret.raise_for_status()
        except HTTPError as http_err:
            raise Exception('Ошибка HTTP: {}'.format(http_err))

    def login(self, login, password):
        r = self.session.post(self.root + '/v1/auth/open',
                              headers=self.headers,
                              json={'login': login, 'password': password})
        self.assert_error(r)

        if r.json()['error_status'] == 1:
            raise OwenException('Ошибка авторизации')
        self.headers.update({'Authorization': 'Bearer ' + r.json()['token']})
        return r.json()

    def devices(self, name_filter=[]):
        """
        Список доступных приборов определяется компанией, к которой принадлежит пользователь.
        Дополнительно по каждому прибору передается мета-информация, такая как пользовательское
        имя, онлайн/оффлайн, местоположение. (если было введено), избранный/не избранный,
        Id категорий, в которые он входит.


        :param number_filter: число, в таком случае будут выведены только приборы, пользовательское
        описание которых подходит под этот фильтр.
        :param company_id: :id, запросить приборы не компании пользователя, а какой-то компании,
        доступной пользователю (если он интегратор).
        :return: массив идентификаторов приборов. Будет выведена инфа только по ним.
        """
        params = {}
        if name_filter:
            params.update({'filter': name_filter})

        r = self.session.post(self.root + '/v1/device/index',
                              headers=self.headers,
                              json=params)
        self.assert_error(r)
        return r.json()

    def device(self, id):
        """
        Возвращает информацию о приборе (тип, настройки, пользовательское название итп) и список
        параметров. Каждый параметр выдаётся сразу со своим дескриптором. Локаль выдаваемых
        дескрипторов берется из настроек пользователя. Также выдаются последние значения
        каждого параметра.
        :param id:
        :return:
        """
        r = self.session.post(self.root + '/v1/device/' + str(id),
                              headers=self.headers,
                              json=[])
        self.assert_error(r)
        return r.json()

    def device_last_dates(self, id):
        """
        Возвращает временные метки основных событий прибора.
        :param id:
        :return:
        {
            "last_dt": "1522309356",
            "last_operative_dt": "1522309256",
            "last_configuration_dt": "1522309466",
            "last_manageable_dt": "1522309416"
        }
        last_dt - временная метка получения последних данных
        last_operative_dt - временная метка получения последних оперативных данных
        last_configuration_dt - временная метка получения последних конфигурационных данных
        last_manageable_dt - временная метка получения последних управляемых данных
        """
        r = self.session.post(self.root + '/v1/device/last-dates/' + str(id),
                              headers=self.headers,
                              json=[])
        self.assert_error(r)
        return r.json()

    def parameters(self, device_id, name_filter):
        dev = self.device(device_id)
        return [p['id'] for p in dev['parameters'] if name_filter in p['name']]

    def last_data(self, ids):
        """
        Возвращает последние полученные данные по переданному списку параметров.
        Для обновления актуальных значений в клиенте настоятельно рекомендуется
        использовать именно этод метод.
        :param ids: список параметров
        :return:
        Возвращается json-массив объектов с полями:
        id - идентификатор параметра
        values - массив с одним объектом.
        d - unix timestamp, когда было получено значение
        v - значение параметра
        e - код ошибки при чтении
            может быть просто числом или "число: пояснение")
        f - отформатированное значение (в т.ч. учитывается код ошибки)
        """
        r = self.session.post(self.root + '/v1/parameters/last-data',
                              headers=self.headers,
                              json={'ids': ids})
        self.assert_error(r)
        return r.json()

    def last_value_info(self, id):
        info = self.last_data([id])
        return info[0]['values'][0]

    def last_value_with_dt(self, id, previous_timestamp=None):
        """
        Возвращает последнее значение параметра.
        Если указать previous_timestamp, то вернет если есть более позднее значение.
        :param id: id параметра
        :param previous_timestamp: если нет нового значения, то NoNewException
        :return:
        """
        info = self.last_value_info(id)

        if info['e']:
            raise OwenException(info['e'])
        else:
            if previous_timestamp and info['d'] <= previous_timestamp:
                raise NoDataException()
            return float(info['v']), info['d']

    def data(self, ids, start_timestamp, end_timestamp, step=1):
        """
        Во входных параметрах передается список идентификаторов параметров, по которым
        требуется получить данные, а также дата и время начала требуемого отрезка, конца
        требуемого отрезка и шаг (если не нужны все данные).

        Система может отказать в выдаче архива если параметров слишком много или требуемый
        интервал слишком длинный. Такая ошибка возвращается как HTTP-код Bad Request.
        :param ids:
        :param start_timestamp:
        :param end_timestamp:
        :return:
        Возвращается json-массив объектов с полями:
        id - идентификатор параметра
        values - массив с одним объектом.
        d - unix timestamp, когда было получено значение
        v - значение параметра (отформатировано как в вебе, может быть числом, строкой. сразу выводится нужная точность согласно единицам измерения, единицы измерения не выводятся)
        e - код ошибки при чтении (текстовое поле, пустая строка - ошибки нет, иначе может быть просто числом или "число: пояснение")
        """
        r = self.session.post(self.root + '/v1/parameters/last-data',
                              headers=self.headers,
                              json={'ids': ids,
                                      'start': dt(start_timestamp),
                                      'end': dt(end_timestamp),
                                      'step': step})
        self.assert_error(r)
        return r.json()

    def forward_data(self, ids, start_timestamp, limit=10):
        """
        Во входных параметрах передается список идентификаторов параметров,
        по которым требуется получить данные, а также дата и время начала требуемого
        отрезка, и максимальное количество возвращаемых записей.

        В остальном запрос аналогичен запросу parameters/data.
        :param ids:
        :param start_timestamp:
        :param limit:
        :return:
        """
        r = self.session.post(self.root + '/v1/parameters/forward-data',
                              headers=self.headers,
                              json={'ids': ids,
                                      'start': dt(start_timestamp),
                                      'limit': limit})
        self.assert_error(r)
        return r.json()

    def backward_data(self, ids, start_timestamp, limit=10):
        """
        Во входных параметрах передается список идентификаторов параметров,
        по которым требуется получить данные, а также дата и время конца
        требуемого отрезка, и максимальное количество возвращаемых записей.

        В остальном запрос аналогичен запросу parameters/data.
        :param ids:
        :param start_timestamp:
        :param limit:
        :return:
        """
        r = self.session.post(self.root + '/v1/parameters/backward-data',
                              headers=self.headers,
                              json={'ids': ids,
                                      'start': dt(start_timestamp),
                                      'limit': limit})
        self.assert_error(r)
        return r.json()

    def events(self, status=0, is_critical=0, is_active=0):
        """
        Получение списка событий, настроенных на приборах компании.
        Отличительная черта пользовательских событий - category_id = null.

        Параметры запроса:

        company_id - идентификатор требуемой компании. Если не указан, подразумевается идентификатор компании, к которой относится сам пользователь.
        status - 0 или 1. Если передан 0, будут возвращены только завершенные события, если 1 - только не завершенные.
        is_critical - 0 или 1. Если передан 0, будут возвращены только некритичные события, если 1 - только критичные.
        is_active - 0 или 1. Если передан 0, будут возвращены только неактивные события, если 1 - только активные.
        :return:
        """
        r = self.session.post(self.root + '/v1/event/list',
                              headers=self.headers,
                              json={'status': status,
                                      'is_critical': is_critical,
                                      'is_active': is_active})
        self.assert_error(r)
        return r.json()

    def devices_events(self, device_ids, status=0, is_critical=0, is_active=0):
        """
        Ответ содержит системные и пользовательские события приборов. Отличительная
        черта пользовательских событий - category_id = null.
        :param device_ids:
        :param status:
        :param is_critical:
        :param is_active:
        :return:
        """
        r = self.session.post(self.root + '/v1/event/list-by-devicest',
                              headers=self.headers,
                              json={'status': status,
                                      'is_critical': is_critical,
                                      'is_active': is_active,
                                      'device_ids': device_ids})
        self.assert_error(r)
        return r.json()

