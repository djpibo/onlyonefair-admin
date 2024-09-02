import time

from api.supabase.model.point import ConsumeInfoDTO
from api.supabase.model.quiz import RankDTO
from api.supabase.repo.common_repo import CommonRepository
from api.supabase.repo.score_repo import ScoreRepository
from common.config import *
from common.util import MapperUtil
from api.google.sheet_client import GoogleSheetsClient


class PointMgr:
    def __init__(self, score_repo:ScoreRepository, common_repo:CommonRepository, google_sheet_client:GoogleSheetsClient):
        self.common_repo = common_repo
        self.google_sheet_client = google_sheet_client
        self.score_repo = score_repo

    def consume_point(self, consume_info:ConsumeInfoDTO):
        self.score_repo.insert_used_point(consume_info)

    def get_latest_consume(self, login_dto):
        return self.score_repo.check_latest_consume(login_dto.peer_id)

    def get_used_point(self, login_dto):
        comsume_info: ConsumeInfoDTO = self.score_repo.get_used_point_by_id(login_dto.peer_id)
        if comsume_info is None:
            return 0
        return sum(item['used_score'] for item in comsume_info)

    def fetch_quiz_point(self, spreadsheet_id, range_name, company_name):
        print(f"[log] {company_name} 퀴즈 점수 시트에서 데이터 가져오는중 ... ")
        values = self.google_sheet_client.fetch_sheet_data(spreadsheet_id, range_name)
        if not values:
            print("No data found.")
            return
        quiz_company_dvcd = self.common_repo.get_company_code(company_name).id

        print(f"[log] {company_name} 퀴즈 점수 데이터베이스에 기록중 ... ")
        self.score_repo.upsert_data_to_supabase(values, quiz_company_dvcd)

    def upload_room_quiz_point(self):
        companies = [
            (LOG_QUIZ_SPREADSHEET_ID, "대한통운"),
            (CJ_QUIZ_SPREADSHEET_ID, "제일제당"),
            (OY_QUIZ_SPREADSHEET_ID, "올리브영"),
            (ENM_QUIZ_SPREADSHEET_ID, "ENM"),
            (ONS_QUIZ_SPREADSHEET_ID, "올리브네트웍스"),
            (CMS_QUIZ_SPREADSHEET_ID, "커머스")
        ]

        while True:
            for spreadsheet_id, company_name in companies:
                self.fetch_quiz_point(spreadsheet_id, SAMPLE_RANGE_NAME, company_name)
            response = self.score_repo.fetch_score_from_supabase()

            print(f"[log] 전 사원 포인트 현황 시트에 기록중... ")
            self.google_sheet_client.batch_update_sheet_data(
                # 실시간 포인트 현황 시트 id
                TOTAL_SCORE_SPREADSHEET_ID,
                # 첫 줄 헤더
                list(RankDTO.__annotations__.keys()),
                # JSON to [[..]]
                MapperUtil.convert_dicts_to_lists(response))

            time.sleep(5)  # 각 회사 처리 후 5초 대기
