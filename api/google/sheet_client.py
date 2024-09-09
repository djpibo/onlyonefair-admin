from typing import List
import pandas as pd

from config.connect import get_google_sheets_service

class GoogleSheetsClient:
    def __init__(self):
        self.service = get_google_sheets_service()
        pass

    def fetch_sheet_data(self, spreadsheet_id, range_name):
        return (self.service.spreadsheets().values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute().get("values", []))

    def fetch_survey_data(self, spreadsheet_id, range_name):
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        df = pd.DataFrame(values, columns=['사번', '회사', '항목'])
        unique_df = df.drop_duplicates(subset=['사번', '항목'])
        count_df = unique_df.groupby('사번').size().reset_index(name='고유 항목 수')

    def clear_sheet_data(self, spreadsheet_id):
        # Clear API 요청 본문 생성
        request_body = {}

        # Clear API 호출
        request = (self.service.spreadsheets().values()
                   .clear(spreadsheetId=spreadsheet_id, range='sheet!A1', body=request_body))
        request.execute()

    def batch_update_sheet_data(self, spreadsheet_id, headers: List[str], data: List[List]):

        print("[log] 실시간 포인트 Sheet 업로드 중.. ")

        # 시트 초기화 후 진행
        self.clear_sheet_data(spreadsheet_id)

        print(f"[log] headers -> {[headers]}")
        values = [headers] + data  # 첫 줄에 헤더 추가
        body = {
            'values': values
        }

        # 데이터 추가
        result = (
            self.service.spreadsheets().values()
            .append(spreadsheetId=spreadsheet_id, range='sheet!A1', valueInputOption='USER_ENTERED', body=body)
            .execute())

        print('{0} cells updated.'.format(result.get('updates').get('updatedCells')))