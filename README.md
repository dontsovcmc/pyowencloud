# pyowencloud
Неофициальный клиент к REST API облака https://owencloud.ru
(Официального не нашёл)

## Установка
pip install pyowencloud

## Пример

### Авторизация
```
cloud = OwenClient()
cloud.login(user, password)
```
### Получение устройства по его имени
```
termometer = cloud.devices(u'термометр')[0]
```
### Последнее значение параметра
```
# Получаем id параметра
temperature_id = cloud.parameters(termometer['id'], u'Температура')[0]

# Запрашиваем последнее значение с временной меткой
value, timestamp = cloud.last_value_with_dt(temperature_id)
```