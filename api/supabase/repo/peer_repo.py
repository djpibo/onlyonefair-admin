from api.supabase.model.point import PeerInfoDTO
from common.util import MapperUtil
from config.connect import connect_supabase

class PeerRepository:
    def __init__(self):
        self.supabase = connect_supabase()

    def fetch_peer_id_from_supabase(self, nfc_id):
        response = (
            self.supabase.table("Peer_Info")
            .select("*")
            .eq("nfc_id", nfc_id)
            .execute()
        )
        return MapperUtil.single_mapper(response, PeerInfoDTO)

    def fetch_peer_info_by_id(self, key_id):
        response = (
            self.supabase.table("Peer_Info")
            .select("*")
            .eq("id", key_id)
            .execute()
        )
        return MapperUtil.single_mapper(response, PeerInfoDTO)

    def check_if_teacher(self, nfc_id):
        response = (
            self.supabase.table("Peer_Info")
            .select("*")
            .eq("nfc_id", nfc_id)
            .execute()
        )
        return MapperUtil.single_mapper(response, PeerInfoDTO)