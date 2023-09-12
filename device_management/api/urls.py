from django.urls import path

from device_management.api.views import senso_datatables, senso_data_interval, senso_sensor_value, \
    senso_sensor_value_last_ten, senso_sensor_value_last_three, config_device_in, get_notifications, \
    update_notifications, createDevice, listDevice, deactivateDevice, activateDevice, set_data_interval, latest_data, \
    last_ten_data, last_four_data, latest_data_pond, last_ten_data_pond, last_four_data_pond, get_device_config

urlpatterns = [
    path('data/datatables/', senso_datatables, name='senso_datatables'),
    path('data-interval/', senso_data_interval, name='senso_data_interval'),
    path('data/sensor-value/', senso_sensor_value, name='senso_sensor_value'),
    path('data/datatables/lastten/', senso_sensor_value_last_ten, name='senso_sensor_value_last_ten'),
    path('data/datatables/lastthree/', senso_sensor_value_last_three, name='senso_sensor_value_last_ten'),

    path('data/latest/<int:pk>/', latest_data, name='latest_data'),
    path('data/last-ten-data/<int:pk>/', last_ten_data, name='last_ten_data'),
    path('data/last-four-data/<int:pk>/', last_four_data, name='last_four_data'),

    path('data/pond/latest/<int:p_id>/', latest_data_pond, name='latest_data'),
    path('data/pond/last-ten-data/<int:p_id>/', last_ten_data_pond, name='last_ten_data'),
    path('data/pond/last-four-data/<int:p_id>/', last_four_data_pond, name='last_four_data'),

    path('config/<int:pk>/', get_device_config, name='get_device_config'),
    path('config/device-in/', config_device_in, name='config_device_in'),
    path('config/interval/', set_data_interval, name='set_data_interval'),

    path('notifications/', get_notifications, name='get_notifications'),
    path('update-notifications/', update_notifications, name='update_notifications'),

    path('create-device/', createDevice, name='create_device'),
    path('list-device/', listDevice, name='list_device'),
    path('deactivate-device/<int:pk>/', deactivateDevice, name='deactivate_device'),
    path('activate-device/<int:pk>/', activateDevice, name='activate_device'),
]
