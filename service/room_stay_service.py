import time

from api.google.sheet_client import GoogleSheetsClient
from api.supabase.model.nfc import EntranceInfoDTO
from api.supabase.model.point import ConsumeInfoDTO, OliveInfoDTO
from api.supabase.model.quiz import RankDTO, ScoreInfoDTO
from api.supabase.repo.common_repo import CommonRepository
from api.supabase.repo.entrance_repo import EntranceRepository
from api.supabase.repo.score_repo import ScoreRepository
from common.config import *
from common.constants import *
from common.util import CommonUtil, MapperUtil


class EnterMgr:
    def __init__(self
                 , entrance_repo: EntranceRepository
                 , common_repo: CommonRepository
                 , score_repo: ScoreRepository):
        self.entrance_repo = entrance_repo
        self.common_repo = common_repo
        self.score_repo = score_repo

    def get_unchecked_exit(self, login_dto):
        return self.entrance_repo.check_exit_yn_the_others(login_dto.peer_id, login_dto.argv_company_dvcd)

    def check_exit_before(self, login_dto):
        return self.entrance_repo.fetch_latest_exit(login_dto.peer_id, login_dto.argv_company_dvcd)

    def set_to_enter(self, login_dto):
        dto = EntranceInfoDTO(
            id= login_dto.peer_id,
            enter_dvcd= ENTER_DVCD_ENTRANCE,
            company_dvcd= login_dto.argv_company_dvcd,
            seqno= 1,
            exit_yn= False
        )
        self.entrance_repo.upsert_entrance_data(dto)

    def set_to_reenter(self, enter_info:EntranceInfoDTO):
        dto = EntranceInfoDTO(
            id= enter_info.id,
            enter_dvcd= ENTER_DVCD_REENTER,
            company_dvcd= enter_info.company_dvcd,
            seqno= enter_info.seqno+1,
            exit_yn= False
        )
        self.entrance_repo.upsert_entrance_data(dto)

    def get_latest_enter(self, login_dto):
        return self.entrance_repo.check_entered_to_entrance_info(login_dto.peer_id, login_dto.argv_company_dvcd)

    def get_latest_exit(self, login_dto):
        return self.entrance_repo.check_exit_to_entrance_info(login_dto.peer_id, login_dto.argv_company_dvcd)

    def validate_if_full(self, login_dto):
        response = self.score_repo.get_exp_score(
            ScoreInfoDTO(id=login_dto.peer_id,
                         quiz_dvcd=QUIZ_DVCD_NFC_EXIST_TIME,
                         company_dvcd=login_dto.argv_company_dvcd,
                         score=99))
        bf_exp_score = sum(item['score'] for item in response)
        return bf_exp_score >= CommonUtil.get_max_time_by_company_dvcd(login_dto.argv_company_dvcd)

    def get_entered_users(self):
        return self.entrance_repo.get_entered_users()

class ExitMgr:
    def __init__(self
                 , entrance_repo: EntranceRepository):
        self.entrance_repo = entrance_repo

    def set_exit_true(self, enter_info_dto:EntranceInfoDTO):
        enter_info_dto.enter_dvcd = ENTER_DVCD_EXIT
        enter_info_dto.exit_yn = True
        self.entrance_repo.upsert_entrance_data(enter_info_dto)

    def set_enter_exit(self, enter_info_dto:EntranceInfoDTO):
        self.entrance_repo.update_enter_exit_true(enter_info_dto)

    def set_force_exit_true(self, enter_info_dto:EntranceInfoDTO):
        enter_info_dto.enter_dvcd = ENTER_DVCD_FORCE_EXIT
        enter_info_dto.exit_yn = True
        self.entrance_repo.upsert_entrance_data(enter_info_dto)


class ScoreMgr:
    def __init__(self,
                 score_repo: ScoreRepository,
                 common_repo: CommonRepository,
                 google_sheet_client:GoogleSheetsClient):
        self.score_repo = score_repo
        self.common_repo = common_repo
        self.google_sheet_client = google_sheet_client

    def set_score(self, score_dto):
        self.score_repo.update_nfc_exist_time_score(score_dto)

    def get_current_point(self, login_dto):
        score_info: ScoreInfoDTO = self.score_repo.get_user_current_point(login_dto.peer_id)
        if score_info is None:
            return 0
        return sum(item['score'] for item in score_info)

    def get_current_olive(self, peer_id):
        return self.score_repo.get_data_olive_info(peer_id)

    def get_exp_score(self, score_dto:ScoreInfoDTO):
        score_info = self.score_repo.get_exp_score(score_dto)
        return sum(item['score'] for item in score_info)

    def get_total_used_score(self, peer_id):
        consume_info: ConsumeInfoDTO = self.score_repo.get_total_used_score(peer_id)
        print(f"[log] consume >> {consume_info} ")
        return sum(item['used_score'] for item in consume_info)

    def set_entrance_point(self, login_dto):
        self.score_repo.update_entrance_score(login_dto.peer_id, login_dto.argv_company_dvcd)

    def validator(self, login_dto):
        self.score_repo.update_entrance_score(login_dto.peer_id, login_dto.argv_company_dvcd)