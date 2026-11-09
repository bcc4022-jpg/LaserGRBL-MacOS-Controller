"""Lightweight interface translations.

Interface strings are written in English in the source and passed through :func:`tr`.
English text is the lookup key, so a missing translation falls back to English.

GRBL state names (``Idle``, ``Run``, ``Alarm`` …), G-code words, and GRBL ``$`` commands
are intentionally left untranslated so that they match controller output and manuals.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterable

SUPPORTED_LANGUAGES = ("en", "ja")
LANGUAGE_ENVIRONMENT_VARIABLE = "LASERGRBL_LANG"

_current_language = "en"

JAPANESE: dict[str, str] = {
    # Header and window
    "A focused GRBL workspace for makers, engravers, and CNC builders.": "ものづくり・レーザー彫刻・CNC のための GRBL 操作ソフト",
    "STOP / RESET": "停止 / リセット",
    "Ready": "準備完了",
    # Connection
    "Connection": "接続",
    "Refresh": "更新",
    "Connect at 115200 baud": "接続する（115200 baud）",
    "Disconnect": "切断",
    "Machine state: {state}": "機械の状態: {state}",
    "Work position  X {x:.3f}   Y {y:.3f}   Z {z:.3f}": "ワーク座標  X {x:.3f}   Y {y:.3f}   Z {z:.3f}",
    "Demo controller (no hardware)": "デモ用コントローラー（機械なし）",
    "Serial device": "シリアル機器",
    "No serial ports found": "シリアルポートが見つかりません",
    "Select a serial port first.": "先にシリアルポートを選んでください。",
    "Connection failed": "接続できませんでした",
    "Detecting GRBL controller…": "GRBL コントローラーを確認しています…",
    "Opened {port} at 115200 baud": "{port} を 115200 baud で開きました",
    "Demo controller connected": "デモ用コントローラーに接続しました",
    "Controller disconnected": "コントローラーを切断しました",
    "GRBL controller connected": "GRBL コントローラーに接続しました",
    "GRBL not detected": "GRBL が見つかりません",
    "A serial device opened, but it did not identify itself as GRBL.": "シリアル機器は開けましたが、GRBL からの応答がありませんでした。",
    "Serial connection lost": "シリアル接続が切れました",
    # Motion
    "Motion": "移動",
    "Jog step": "移動量",
    "Home": "原点復帰",
    "Unlock": "ロック解除",
    "Set work zero": "ワーク原点を設定",
    "Set the current position as X0 Y0 Z0 in the active work coordinate system?": "いまの位置を、使用中のワーク座標系の X0 Y0 Z0 にしますか？",
    # Laser
    "Laser and feed": "レーザーと送り速度",
    "Maximum power": "最大出力",
    "Feed rate": "送り速度",
    "Enable low-power test control": "低出力テストを有効にする",
    "Hold for 1% laser test": "押している間だけ 1% でテスト照射",
    # Artwork
    "Artwork and G-code": "画像と G-code",
    "Open image": "画像を開く",
    "Open G-code": "G-code を開く",
    "No artwork selected": "画像が選ばれていません",
    "Width": "幅",
    "Height": "高さ",
    "Resolution": "解像度",
    "Threshold": "しきい値",
    "Generate G-code": "G-code を作成",
    "Save": "保存",
    "Open artwork": "画像を開く",
    "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)": "画像 (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)",
    "G-code (*.gcode *.nc *.tap *.txt);;All files (*)": "G-code (*.gcode *.nc *.tap *.txt);;すべてのファイル (*)",
    "G-code (*.gcode);;Text (*.txt)": "G-code (*.gcode);;テキスト (*.txt)",
    "G-code generation failed": "G-code を作成できませんでした",
    "Generated {count:,} G-code lines": "G-code を {count:,} 行作成しました",
    "Open failed": "開けませんでした",
    "Save G-code": "G-code を保存",
    "Save failed": "保存できませんでした",
    # Job
    "Job": "ジョブ",
    "No active job": "実行中のジョブはありません",
    "Start job": "ジョブを開始",
    "Pause": "一時停止",
    "Resume": "再開",
    "Abort": "中止",
    "No executable G-code was found.": "実行できる G-code がありません。",
    "Start laser job": "レーザージョブを開始",
    "Stream {total:,} commands to the connected controller?": "接続中のコントローラーに {total:,} 個の命令を送りますか？",
    "Confirm ventilation, eye protection, focus, and a clear machine area before continuing.": "続ける前に、換気・保護メガネ・焦点、機械のまわりに物がないことを確かめてください。",
    "Started {total:,}-line job": "{total:,} 行のジョブを開始しました",
    "Feed hold requested": "一時停止（フィードホールド）を送りました",
    "Cycle resume requested": "再開（サイクルスタート）を送りました",
    "Abort job": "ジョブを中止",
    "Immediately issue feed hold and a GRBL soft reset?": "すぐにフィードホールドと GRBL のソフトリセットを送りますか？",
    "Job aborted": "ジョブを中止しました",
    "Job aborted with feed hold and soft reset": "フィードホールドとソフトリセットでジョブを中止しました",
    "calculating": "計算中",
    "{done:,} / {total:,} commands · {remaining} remaining": "{done:,} / {total:,} 命令 · 残り {remaining}",
    "Completed in {duration}": "{duration} で完了しました",
    "Job complete": "ジョブ完了",
    "All G-code commands were acknowledged in {duration}.": "すべての G-code 命令が {duration} で受け付けられました。",
    "Job stopped": "ジョブが止まりました",
    "GRBL reported: {line}": "GRBL からの報告: {line}",
    "Serial write failed.": "シリアルへの書き込みに失敗しました。",
    "Active job": "実行中のジョブ",
    "Abort the active job and quit?": "実行中のジョブを中止して終了しますか？",
    # Commands
    "Not connected": "接続されていません",
    "Connect to a GRBL controller first.": "先に GRBL コントローラーに接続してください。",
    "Job active": "ジョブ実行中",
    "Pause or abort the current job before sending manual commands.": "手動で命令を送る前に、いまのジョブを一時停止するか中止してください。",
    "Send failed": "送信できませんでした",
    # Workspace
    "Fit preview": "全体を表示",
    "Path preview": "経路プレビュー",
    "Open, generate, or paste G-code here.": "ここに G-code を開く・作成する・貼り付けることができます。",
    "Console": "コンソール",
    "G-code": "G-code",
    "Previewed {count:,} motion segments": "{count:,} 本の移動経路を表示しました",
    "Previewed {count:,} motion segments at 1:{stride} detail": "{count:,} 本の移動経路を 1/{stride} に間引いて表示しました",
    # Menus
    "File": "ファイル",
    "Open Image…": "画像を開く…",
    "Open G-code…": "G-code を開く…",
    "Save G-code…": "G-code を保存…",
    "Quit": "終了",
    "Machine": "機械",
    "Refresh Ports": "ポートを更新",
    "Request Settings ($$)": "設定を読み出す ($$)",
    "Request Parser State ($G)": "パーサーの状態を読み出す ($G)",
    "Soft Reset": "ソフトリセット",
    "Help": "ヘルプ",
    "Laser Safety": "レーザーの安全",
    "About": "このソフトについて",
    "Laser safety": "レーザーの安全",
    "Never operate a laser unattended. Use wavelength-rated eye protection, effective ventilation, a fire-resistant enclosure, and a physical emergency stop. Test with minimum power first. Software controls are not a substitute for hardware safety systems.": (
        "レーザーを動かしている間は、その場を離れないでください。波長に合った保護メガネ、十分な換気、"
        "燃えにくい囲い、物理的な非常停止スイッチを使ってください。まず最小の出力で試してください。"
        "ソフトウェアの操作は、機械側の安全装置の代わりにはなりません。"
    ),
    "About LaserGRBL for macOS": "LaserGRBL for macOS について",
    "An open-source desktop controller for GRBL-compatible laser engravers and CNC machines.": "GRBL 互換のレーザー彫刻機・CNC 用の、オープンソースの操作ソフトです。",
    # App-internal connection states shown in the status chip
    "Disconnected": "未接続",
    "Detecting": "確認中",
    # Errors raised by the core modules
    "Cannot replace G-code while a job is active.": "ジョブの実行中は G-code を入れかえられません。",
    "No G-code is loaded.": "G-code が読み込まれていません。",
    "Artwork dimensions must be between 0 and 1,000 mm.": "画像の大きさは 0〜1,000 mm にしてください。",
    "Resolution must be between 1 and 20 pixels per millimeter.": "解像度は 1〜20 px/mm にしてください。",
    "Threshold must be between 0 and 255.": "しきい値は 0〜255 にしてください。",
    "Maximum laser power must be positive.": "最大出力は 0 より大きくしてください。",
    "Feed rate must be positive.": "送り速度は 0 より大きくしてください。",
}

# Messages produced by the core modules that contain values. Each pattern is matched against
# the full English message; named groups are passed to the translated template.
_JAPANESE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"The selected size and resolution produce (?P<points>[\d,]+) points; the safety limit is (?P<limit>[\d,]+)\."
        ),
        "この大きさと解像度だと {points} 点になり、安全のための上限 {limit} 点をこえます。",
    ),
]

_CATALOGS: dict[str, dict[str, str]] = {"ja": JAPANESE}
_PATTERNS: dict[str, list[tuple[re.Pattern[str], str]]] = {"ja": _JAPANESE_PATTERNS}


def normalize_language(tag: str | None) -> str | None:
    """Map a locale tag such as ``ja_JP.UTF-8`` or ``ja-JP`` to a supported language code."""
    if not tag:
        return None
    code = re.split(r"[-_.@]", tag.strip().lower(), maxsplit=1)[0]
    return code if code in SUPPORTED_LANGUAGES else None


def detect_language(preferred: Iterable[str] = (), environment: dict[str, str] | None = None) -> str:
    """Pick the interface language.

    ``LASERGRBL_LANG`` wins when it names a supported language. Otherwise the first supported entry
    of ``preferred`` (for example ``QLocale.system().uiLanguages()``) is used, falling back to English.
    """
    environment = os.environ if environment is None else environment
    forced = normalize_language(environment.get(LANGUAGE_ENVIRONMENT_VARIABLE))
    if forced:
        return forced
    for tag in preferred:
        language = normalize_language(tag)
        if language:
            return language
    return "en"


def set_language(language: str) -> None:
    global _current_language
    _current_language = language if language in SUPPORTED_LANGUAGES else "en"


def current_language() -> str:
    return _current_language


def tr(text: str, /, **values: object) -> str:
    """Translate ``text`` into the current language and fill ``{placeholders}`` from ``values``."""
    template = _CATALOGS.get(_current_language, {}).get(text, text)
    return template.format(**values) if values else template


def tr_message(message: str) -> str:
    """Translate a message that was produced elsewhere (for example an exception), if it is known."""
    catalog = _CATALOGS.get(_current_language)
    if catalog is None:
        return message
    if message in catalog:
        return catalog[message]
    for pattern, template in _PATTERNS.get(_current_language, []):
        match = pattern.fullmatch(message)
        if match:
            return template.format(**match.groupdict())
    return message
