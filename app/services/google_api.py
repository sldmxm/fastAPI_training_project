from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle
from fastapi import HTTPException

from app.core.config import settings

REPORT_DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'
SHEETS_VERSION = 'v4'
# оставил, иначе долго добираться для проверки достаточности строк
# ну или неправильно понял комментарий
# "Недопустимо зашивать важные для проекта константы: габариты таблицы."
REPORT_ROWS_COUNT = 100
REPORT_COLUMNS_COUNT = 3
REPORT_SPREADSHEET_BODY = {
    'properties': {'title': 'QRKot отчет на %s',
                   'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Лист1',
                               'gridProperties': {'rowCount': REPORT_ROWS_COUNT,
                                                  'columnCount': REPORT_COLUMNS_COUNT}}}]
}
REPORT_TITLE_ROWS = [
    ['Отчет от', '%s'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]


def spreadsheet_body_generate(report_date: datetime = None) -> dict:
    if not report_date:
        report_date = datetime.now().strftime(REPORT_DATETIME_FORMAT)
    spreadsheet_body = deepcopy(REPORT_SPREADSHEET_BODY)
    spreadsheet_body['properties']['title'] %= report_date
    return spreadsheet_body


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    service = await wrapper_services.discover('sheets', SHEETS_VERSION)
    spreadsheet_body = spreadsheet_body_generate()
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
    service = await wrapper_services.discover('sheets', 'v4')
    now_date_time = datetime.now().strftime(REPORT_DATETIME_FORMAT)
    table_values = deepcopy(REPORT_TITLE_ROWS)
    table_values[0][1] %= now_date_time
    for project, duration in projects_and_durations:
        new_row = [project.name, str(duration), project.description]
        table_values.append(new_row)

    if (
            len(table_values) > REPORT_ROWS_COUNT or
            len(table_values[0]) > REPORT_COLUMNS_COUNT
    ):
        raise HTTPException(
            status_code=400,
            detail='Данные превышают допустимый диапазон ячеек'
        )

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=r'A1:C100',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
