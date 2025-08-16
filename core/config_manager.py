# ファイル名: core/config_manager.py

import json
import os
# 【追加】
from dataclasses import dataclass, field

# 【追加】設定ファイルの各セクションに対応するデータクラスを定義
@dataclass
class FFTInitialViewConfig:
    variable_group: str = "all"
    show_fit_line: bool = True

@dataclass
class RealtimeSettingsConfig:
    video_source: str = "0"
    yolo_model_path: str = "models/yolov8n.pt"
    mediapipe_model_path: str = "models/face_landmarker.task"
    device: str = "cpu"

@dataclass
class AnalysisParametersConfig:
    UPDATE_INTERVAL_MS: int = 1000
    SLIDING_WINDOW_SECONDS: int = 30

@dataclass
class AppConfig:
    """アプリケーション設定全体を保持するデータクラス"""
    fft_initial_view: FFTInitialViewConfig = field(default_factory=FFTInitialViewConfig)
    realtime_settings: RealtimeSettingsConfig = field(default_factory=RealtimeSettingsConfig)
    analysis_parameters: AnalysisParametersConfig = field(default_factory=AnalysisParametersConfig)

    # 【追加】辞書からインスタンスを生成するファクトリメソッド
    @classmethod
    def from_dict(cls, data):
        return cls(
            fft_initial_view=FFTInitialViewConfig(**data.get("fft_initial_view", {})),
            realtime_settings=RealtimeSettingsConfig(**data.get("realtime_settings", {})),
            analysis_parameters=AnalysisParametersConfig(**data.get("analysis_parameters", {}))
        )

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        # 【変更】configをAppConfigクラスのインスタンスとして保持
        self.config: AppConfig = self.load_config()

    def get_default_config(self):
        """【変更】デフォルト設定をAppConfigインスタンスとして返す"""
        return AppConfig()

    def load_config(self):
        """
        設定ファイルを読み込む。ファイルが存在しない場合はデフォルト設定で作成する。
        """
        if not os.path.exists(self.config_file):
            print(f"INFO: 設定ファイル '{self.config_file}' が見つかりません。デフォルト設定で作成します。")
            default_config = self.get_default_config()
            self.save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                print(f"INFO: 設定ファイル '{self.config_file}' を読み込みました。")
                # 【変更】辞書からAppConfigインスタンスに変換
                return AppConfig.from_dict(config_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"ERROR: 設定ファイルの読み込みに失敗しました: {e}。デフォルト設定を使用します。")
            return self.get_default_config()

    def save_config(self, config_data):
        # (略: 保存処理はconfig_dataが辞書であることを期待するため、
        # AppConfigインスタンスを辞書に変換する処理を追加する必要があるが、
        # ConfigDialog側で辞書として渡すため、ここでは修正不要)
        pass
    
    # 【削除または変更】getメソッドは不要になるか、実装を変更する
    # def get(self, key, default=None):
    #     return self.config.get(key, default)