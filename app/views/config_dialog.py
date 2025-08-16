# ファイル名: views/config_dialog.py (新規作成)

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from core.config_manager import AppConfig, FFTInitialViewConfig, RealtimeSettingsConfig, AnalysisParametersConfig
import json # for converting back to dict

class ConfigDialog(tk.Toplevel):
    def __init__(self, parent, config_manager):
        """
        設定ダイアログのウィンドウを作成する。

        Args:
            parent: 親ウィンドウ (AppMainWindow)
            config_manager: 設定を管理するConfigManagerのインスタンス
        """
        super().__init__(parent)
        self.transient(parent) # 親ウィンドウの上に表示されるようにする
        self.grab_set() # このウィンドウにフォーカスを固定する

        self.title("設定")
        self.geometry("400x300")
        
        self.config_manager = config_manager
        # 【変更】辞書ではなく、AppConfigオブジェクトを直接扱う
        self.config_data = self.config_manager.config

        # --- UIで使う変数 ---
        # FFT
        self.fft_variable_group = tk.StringVar(value=self.config_data.fft_initial_view.variable_group)
        self.fft_show_fit_line = tk.BooleanVar(value=self.config_data.fft_initial_view.show_fit_line)
        # 【追加】Realtime
        self.rt_video_source = tk.StringVar(value=self.config_data.realtime_settings.video_source)
        self.rt_yolo_path = tk.StringVar(value=self.config_data.realtime_settings.yolo_model_path)
        self.rt_mediapipe_path = tk.StringVar(value=self.config_data.realtime_settings.mediapipe_model_path)
        self.rt_device = tk.StringVar(value=self.config_data.realtime_settings.device)
        # 【追加】Analysis
        self.an_update_interval = tk.IntVar(value=self.config_data.analysis_parameters.UPDATE_INTERVAL_MS)
        self.an_sliding_window = tk.IntVar(value=self.config_data.analysis_parameters.SLIDING_WINDOW_SECONDS)

        self._setup_ui()

    def _setup_ui(self):
        """UI要素を作成して配置する"""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Notebookで設定をタブ分け ---
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- 1. FFTタブ ---
        fft_tab = ttk.Frame(notebook, padding=10)
        notebook.add(fft_tab, text="FFT表示")
        fft_frame = ttk.LabelFrame(fft_tab, text="FFTグラフの初期表示設定", padding=10)
        fft_frame.pack(fill=tk.X, pady=5)

        # 変数グループのラジオボタン
        ttk.Label(fft_frame, text="変数グループ:").pack(anchor='w')
        ttk.Radiobutton(fft_frame, text="全て", variable=self.fft_variable_group, value="all").pack(anchor='w', padx=20)
        ttk.Radiobutton(fft_frame, text="感情のみ", variable=self.fft_variable_group, value="emotion").pack(anchor='w', padx=20)
        ttk.Radiobutton(fft_frame, text="行動のみ", variable=self.fft_variable_group, value="behavior").pack(anchor='w', padx=20)

        # 近似直線のチェックボックス
        ttk.Checkbutton(
            fft_frame,
            text="近似直線を表示する",
            variable=self.fft_show_fit_line
        ).pack(anchor='w', pady=(10, 0))

        # --- 2. リアルタイム処理タブ ---
        rt_tab = ttk.Frame(notebook, padding=10)
        notebook.add(rt_tab, text="リアルタイム処理")
        rt_frame = ttk.LabelFrame(rt_tab, text="リアルタイム処理設定", padding=10)
        rt_frame.pack(fill=tk.X, pady=5)

        ttk.Label(rt_frame, text="映像ソース:").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(rt_frame, textvariable=self.rt_video_source).grid(row=0, column=1, sticky='we', pady=2)

        ttk.Label(rt_frame, text="YOLOモデルパス:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(rt_frame, textvariable=self.rt_yolo_path).grid(row=1, column=1, sticky='we', pady=2)
        
        ttk.Label(rt_frame, text="MediaPipeモデルパス:").grid(row=2, column=0, sticky='w', pady=2)
        ttk.Entry(rt_frame, textvariable=self.rt_mediapipe_path).grid(row=2, column=1, sticky='we', pady=2)
        
        ttk.Label(rt_frame, text="デバイス:").grid(row=3, column=0, sticky='w', pady=2)
        ttk.Entry(rt_frame, textvariable=self.rt_device).grid(row=3, column=1, sticky='we', pady=2)
        rt_frame.columnconfigure(1, weight=1)

        # --- 3. 解析パラメータタブ ---
        an_tab = ttk.Frame(notebook, padding=10)
        notebook.add(an_tab, text="解析パラメータ")
        an_frame = ttk.LabelFrame(an_tab, text="解析パラメータ設定", padding=10)
        an_frame.pack(fill=tk.X, pady=5)

        ttk.Label(an_frame, text="UI更新間隔 (ms):").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(an_frame, textvariable=self.an_update_interval).grid(row=0, column=1, sticky='we', pady=2)

        ttk.Label(an_frame, text="スライディング窓 (秒):").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(an_frame, textvariable=self.an_sliding_window).grid(row=1, column=1, sticky='we', pady=2)
        an_frame.columnconfigure(1, weight=1)

        # --- 下部のボタンフレーム (変更なし) ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="キャンセル", command=self._on_cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="保存", command=self._on_save).pack(side=tk.RIGHT)


    def _on_save(self):
        """「保存」ボタンが押されたときの処理"""
        # 【変更】UIの値からAppConfigオブジェクトを再構築
        try:
            updated_config = AppConfig(
                fft_initial_view=FFTInitialViewConfig(
                    variable_group=self.fft_variable_group.get(),
                    show_fit_line=self.fft_show_fit_line.get()
                ),
                realtime_settings=RealtimeSettingsConfig(
                    video_source=self.rt_video_source.get(),
                    yolo_model_path=self.rt_yolo_path.get(),
                    mediapipe_model_path=self.rt_mediapipe_path.get(),
                    device=self.rt_device.get()
                ),
                analysis_parameters=AnalysisParametersConfig(
                    UPDATE_INTERVAL_MS=self.an_update_interval.get(),
                    SLIDING_WINDOW_SECONDS=self.an_sliding_window.get()
                )
            )
            
            # dataclassesを辞書に変換して保存
            import dataclasses
            config_dict = dataclasses.asdict(updated_config)

            self.config_manager.save_config(config_dict)
            self.destroy()
        except tk.TclError as e:
            messagebox.showerror("入力エラー", f"数値項目に正しい数値を入力してください。\n{e}")
        except Exception as e:
            messagebox.showerror("保存エラー", f"設定の保存中にエラーが発生しました:\n{e}")

    def _on_cancel(self):
        """「キャンセル」ボタンが押されたときの処理"""
        self.destroy() # 何もせずウィンドウを閉じる