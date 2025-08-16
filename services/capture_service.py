# services/capture_service.py

import multiprocessing
import time
import logging
import queue

# Orchestratorをインポート
from .realtime_orchestrator import RealtimeOrchestrator
from .process_utils import Status, StatusMessage

logger = logging.getLogger(__name__)

class CaptureService:
    def __init__(self, data_queue: multiprocessing.Queue, frame_queue: multiprocessing.Queue, status_queue: multiprocessing.Queue, config: dict):
        self.data_queue = data_queue
        self.frame_queue = frame_queue
        # 【追加】
        self.status_queue = status_queue
        self.config = config
        self._process = None
        self.running = multiprocessing.Event()

    def start(self):
        if self._process and self._process.is_alive():
            logger.info("CaptureServiceは既に実行中です。")
            return

        self.running.set()
        self._process = multiprocessing.Process(
            target=self._run_capture_loop,
            # 【変更】status_queueを渡す
            args=(self.data_queue, self.frame_queue, self.status_queue, self.running, self.config),
            daemon=True
        )
        self._process.start()
        logger.info("CaptureServiceを開始しました。")

    def stop(self):
        if self.running:
            self.running.clear()
        if self._process:
            self._process.join(timeout=3) # 少し長めに待つ
            if self._process.is_alive():
                logger.warning("CaptureServiceが時間内に終了せず、強制終了します。")
                self._process.terminate()
            logger.info("CaptureServiceを停止しました。")
        self._process = None

    @staticmethod
    def _run_capture_loop(data_queue, frame_queue, status_queue, running_event, config):
        """【別プロセス】Orchestratorを初期化してループ実行する"""
        logger.info("(別プロセス) 映像処理ループを開始します。")
        try:
            orchestrator = RealtimeOrchestrator(config)
        except Exception as e:
            logger.error(f"(別プロセス) Orchestratorの初期化に失敗: {e}")
            # 【追加】初期化失敗をGUIに通知
            status_queue.put(StatusMessage(Status.ERROR, f"Orchestratorの初期化に失敗しました:\n{e}"))
            return

        while running_event.is_set():
            try:
                # (略: 1フレーム処理を実行)
                feature_packet, annotated_frame = orchestrator.process_one_frame()

                if feature_packet is None and annotated_frame is None:
                    logger.info("(別プロセス) 映像ソースの終端に達したため、ループを終了します。")
                    # 【追加】再生完了をGUIに通知
                    status_queue.put(StatusMessage(Status.COMPLETED, "映像ソースの再生が完了しました。"))
                    break
                # (略: キューへの送信処理)

            except Exception as e:
                logger.error(f"(別プロセス) フレーム処理中にエラーが発生: {e}")
                # 【追加】実行時エラーをGUIに通知
                status_queue.put(StatusMessage(Status.ERROR, f"フレーム処理中にエラーが発生しました:\n{e}"))
                time.sleep(1)

        orchestrator.release()
        logger.info("(別プロセス) 映像処理ループが正常に終了しました。")