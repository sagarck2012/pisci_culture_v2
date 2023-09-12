from datetime import datetime

from device_management.models import Notification


def createNotification(level, topic, message, device, c_date, value):
    Notification.objects.create(
        level=level,
        topic=topic,
        message=message,
        seen_status=False,
        device_reg=device,
        created_at=datetime.now(),
        notification_at=datetime.strptime(c_date, "%d-%m-%Y %H:%M:%S"),
        topic_value=value
    )


def checkDO(item, device_reg):
    if item['value'] > 9.0:
        createNotification('Danger', 'DO', 'DO is getting higher.', device_reg, item["created_date"], item['value'])
    elif item['value'] > 8.4:
        createNotification('Warning', 'DO', 'DO is getting higher.', device_reg, item["created_date"], item['value'])
    elif item['value'] < 4.5:
        createNotification('Warning', 'DO', 'DO is getting lower.', device_reg, item["created_date"], item['value'])
    elif item['value'] < 4.0:
        createNotification('Danger', 'DO', 'DO is getting lower.', device_reg, item["created_date"], item['value'])


def checkPH(item, device_reg):
    if item['value'] > 7.8:
        createNotification('Danger', 'PH', 'PH is getting higher.', device_reg, item["created_date"], item['value'])
    elif item['value'] > 7.5:
        createNotification('Warning', 'PH', 'PH is getting higher.', device_reg, item["created_date"], item['value'])
    elif item['value'] < 6.5:
        createNotification('Warning', 'PH', 'PH is getting lower.', device_reg, item["created_date"], item['value'])
    elif item['value'] < 6.2:
        createNotification('Danger', 'PH', 'PH is getting lower.', device_reg, item["created_date"], item['value'])


def checkTemp(item, device_reg):
    if item['value'] > 30:
        createNotification('Danger', 'Temp', 'Temperature is getting higher.', device_reg, item["created_date"], item['value'])
    elif item['value'] > 27:
        createNotification('Warning', 'Temp', 'Temperature is getting higher.', device_reg, item["created_date"], item['value'])
    elif item['value'] < 24:
        createNotification('Warning', 'Temp', 'Temperature is getting lower.', device_reg, item["created_date"], item['value'])
    elif item['value'] < 21:
        createNotification('Danger', 'Temp', 'Temperature is getting lower.', device_reg, item["created_date"], item['value'])
