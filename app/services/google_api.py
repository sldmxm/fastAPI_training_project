from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings

DATETIME_FORMAT_FOR_REPORT = '%Y/%m/%d %H:%M:%S'
REPORT_ROWS = 100
REPORT_COLUMNS = 3
SHEETS_VERSION = 'v4'


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(DATETIME_FORMAT_FOR_REPORT)
    service = await wrapper_services.discover('sheets', SHEETS_VERSION)
    spreadsheet_body = {
        'properties': {'title': f'QRKot отчет на {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист1',
                                   'gridProperties': {'rowCount': REPORT_ROWS,
                                                      'columnCount': REPORT_COLUMNS}}}]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects_and_durations: list,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(DATETIME_FORMAT_FOR_REPORT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        ['Отчет от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for project, duration in projects_and_durations:
        new_row = [project.name, str(duration), project.description]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:C100',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
