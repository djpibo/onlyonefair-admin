from api.supabase.model.common import LoginDTO
from api.supabase.model.nfc import CountInfoDTO
from api.supabase.repo.common_repo import CommonRepository
from api.supabase.repo.peer_repo import PeerRepository

class CommonMgr:
    def __init__(self, common_repo:CommonRepository, peer_repo:PeerRepository):
        self.common_repo = common_repo
        self.peer_repo = peer_repo

    def get_cmn_cd(self, cmn_nm, cmn_desc):
        return self.common_repo.get_cmn_code_with_nm_desc(cmn_nm, cmn_desc).id

    def get_peer_id(self, nfc_uid):
        return self.peer_repo.fetch_peer_id_from_supabase(nfc_uid).id

    def get_peer_name(self, nfc_uid):
        return self.peer_repo.fetch_peer_id_from_supabase(nfc_uid).name

    def get_peer_company(self, nfc_uid):
        return self.peer_repo.fetch_peer_id_from_supabase(nfc_uid).company

    def get_peer_name_by_id(self, key_id):
        return self.peer_repo.fetch_peer_info_by_id(key_id).name

    def get_common_desc(self, company_dvcd):
        return self.common_repo.get_common_by_cmn_id(company_dvcd).cmn_desc

    def count_up(self, nfc_uid):
        self.common_repo.insert_tag_count(CountInfoDTO(id=self.get_peer_id(nfc_uid)))

    def validate_teacher(self, nfc_id):
        grade = self.peer_repo.check_if_teacher(nfc_id).grade
        if grade == 1:
            return True
        return False

    def login_setter(self, argv1, argv2, nfc_uid):
        comp_dvcd = self.get_cmn_cd("회사명", argv1)
        enter_dvcd = self.get_cmn_cd("입퇴장구분코드", argv2)
        peer_company = self.get_peer_company(nfc_uid)
        peer_name = self.get_peer_name(nfc_uid)
        peer_id = self.get_peer_id(nfc_uid)
        return LoginDTO(peer_id=peer_id, argv_company_dvcd=comp_dvcd, peer_name=peer_name, peer_company=peer_company, enter_dvcd=enter_dvcd)