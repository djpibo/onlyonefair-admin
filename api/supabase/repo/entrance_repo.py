from api.supabase.model.nfc import EntranceInfoDTO
from common import constants
from common.constants import ENTER_DVCD_ENTRANCE, ENTER_DVCD_EXIT
from common.util import MapperUtil
from config.connect import connect_supabase


class EntranceRepository:
    def __init__(self):
        self.supabase = connect_supabase()

    def update_enter_exit_true(self, entrance_info_dto:EntranceInfoDTO):

        response = (
            self.supabase.table("Entrance_Info")
            .update({"exit_yn": True})
            .eq("id", entrance_info_dto.id)
            .eq("company_dvcd", entrance_info_dto.company_dvcd)
            .eq("enter_dvcd", entrance_info_dto.enter_dvcd)
            .eq("seqno", entrance_info_dto.seqno)
            .execute()
        )

    def upsert_entrance_data(self, entrance_info_dto:EntranceInfoDTO):

        data_to_upsert = [
            {
                "id": entrance_info_dto.id
                , "company_dvcd": entrance_info_dto.company_dvcd
                , "enter_dvcd": entrance_info_dto.enter_dvcd
    #            , "created_at": datetime.now(timezone.utc)
                , "seqno" : entrance_info_dto.seqno
                , "exit_yn": entrance_info_dto.exit_yn
            }
        ]
        query = self.supabase.table("Entrance_Info")
        if entrance_info_dto.enter_dvcd == constants.ENTER_DVCD_ENTRANCE:
            query = query.upsert(data_to_upsert, ignore_duplicates = True)
        else:
            query = query.upsert(data_to_upsert)
        query.execute()

    def set_exit_true(self, entrance_info_dto:EntranceInfoDTO):
            query = (
                self.supabase.table("Entrance_Info")
                .update({"exit_yn": True})
                .eq("id", entrance_info_dto.id)
                .eq("company_dvcd", entrance_info_dto.company_dvcd)
                .eq("enter_dvcd", entrance_info_dto.enter_dvcd)
                .eq("seqno", entrance_info_dto.seqno)
                .execute()
            )

    # 재입장 확인 : 지금 입장할 부스에서 한 번이라도 퇴장한 적이 있는 경우, 퇴장 여러번 한 경우 복수의 row가 나올 수 있음
    # 최초입장인 경우, 퇴장한 적이 없기 때문에 null
    def fetch_latest_exit(self, peer_id, company_dvcd):
        response = (
            self.supabase.table("Entrance_Info")
            .select("*")
            .eq("id", peer_id)
            .eq("company_dvcd", company_dvcd)
            .eq("exit_yn", True)
            .order("seqno", desc="True")
            .limit(1)
            .execute()
        )
        return MapperUtil.single_mapper(response, EntranceInfoDTO)

    # 다른 부스에서 퇴장을 찍지 않고 들어오는 경우
    def check_exit_yn_the_others(self, peer_id, company_dvcd):
        response = (
            self.supabase.table("Entrance_Info")
            .select("*")
            .eq("id", peer_id)
            .neq("company_dvcd", company_dvcd)
            .eq("exit_yn", False)
            .execute()
        )
        return MapperUtil.single_mapper(response, EntranceInfoDTO)

    # 가장 최근에 입장한 정보를 가져오기(시간 계산) + 퇴장-검증에서도 사용
    def check_entered_to_entrance_info(self, peer_id, company_dvcd):
        response = (
            self.supabase.table("Entrance_Info")
            .select("*")
            .eq("id", peer_id)
            .eq("company_dvcd", company_dvcd)
            .eq("exit_yn", False) # 퇴장 전에는 False 이므로
            .in_("enter_dvcd", [10, 12]) # 입장 or 재입장
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return MapperUtil.single_mapper(response, EntranceInfoDTO)

    # 연속 퇴장 여부 확인
    def check_exit_to_entrance_info(self, peer_id, company_dvcd):
        response = (
            self.supabase.table("Entrance_Info")
            .select("*")
            .eq("id", peer_id)
            .eq("company_dvcd", company_dvcd)
            .eq("exit_yn", True)
            .eq("enter_dvcd", ENTER_DVCD_EXIT)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return MapperUtil.single_mapper(response, EntranceInfoDTO)

    def get_entered_users(self):
        response = (
            self.supabase.table("Entrance_Info")
            .select("*")
            .eq("exit_yn", False)
            .in_("enter_dvcd", [10, 12]) # 입장 or 재입장
            .execute()
        )
        return MapperUtil.multi_mapper(response, EntranceInfoDTO)