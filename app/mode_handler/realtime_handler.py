# app/mode_handler/realtime_handler.py

import queue
from .mode_handler_base import ModeHandlerBase
from services.capture_service import CaptureService
from core.config_manager import RealtimeSettingsConfig
import dataclasses

class RealtimeHandler(ModeHandlerBase):
    """リアルタイム解析モードのロジックを担当するクラス。"""
    def __init__(self, controller):
        super().__init__(controller)
        self.data_queue = self.controller.app.data_queue
        self.frame_queue = self.controller.app.frame_queue
        self.status_queue = self.controller.status_queue
        self.capture_service = None

    def _start_specifics(self):
        """リアルタイムモード固有の開始処理"""
        rt_config_obj = self.controller.config_manager.config.realtime_settings
        rt_config_dict = dataclasses.asdict(rt_config_obj)
        
        self.capture_service = CaptureService(self.data_queue, self.frame_queue, self.status_queue, rt_config_dict)
        self.capture_service.start()
        self.model.full_history = []
        self.model.active_ids = []
        print("リアルタイム解析を開始します。")

    def _stop_specifics(self):
        """リアルタイムモード固有の停止処理"""
        if self.capture_service:
            self.capture_service.stop()
        print("リアルタイム解析を停止しました。")

    def _toggle_pause_specifics(self):
        """リアルタイムモード固有の一時停止/再開処理"""
        if self.is_paused:
            print("リアルタイム解析を一時停止しました。")
        else:
            print("リアルタイム解析を再開しました。")

    def get_next_data_packet(self):
        try:
            # キューからデータをノンブロッキングで取得
            packet = self.data_queue.get_nowait()
            
            # 新しいIDが登場したら、active_idsに追加する
            new_ids = [k for k in packet.keys() if k.startswith('ID_') and k not in self.model.active_ids]
            if new_ids:
                self.model.active_ids.extend(new_ids)
                self.model.active_ids.sort() # 順番を安定させる
            
            return packet
        except queue.Empty:
            return None # キューが空なら何もしない

    def get_latest_frame(self):
        """映像フレームキューから最新のフレームを1つだけ取得する"""
        frame = None
        while not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get_nowait()
            except queue.Empty:
                break
        return frame




