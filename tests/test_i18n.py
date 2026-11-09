import ast
import string
from pathlib import Path

import pytest

from lasergrbl_macos import i18n
from lasergrbl_macos.gcode import RasterSettings, image_to_gcode

APP_SOURCE = Path(__file__).resolve().parents[1] / "src" / "lasergrbl_macos" / "app.py"


@pytest.fixture(autouse=True)
def reset_language():
    yield
    i18n.set_language("en")


def _tr_keys() -> set[str]:
    keys: set[str] = set()
    for node in ast.walk(ast.parse(APP_SOURCE.read_text(encoding="utf-8"))):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "tr"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            keys.add(node.args[0].value)
    return keys


def _placeholders(template: str) -> set[str]:
    return {field for _, field, _, _ in string.Formatter().parse(template) if field}


def test_every_interface_string_has_a_japanese_translation() -> None:
    keys = _tr_keys()
    assert len(keys) > 80
    missing = sorted(keys - i18n.JAPANESE.keys())
    assert missing == []


def test_translations_keep_the_same_placeholders() -> None:
    for english, japanese in i18n.JAPANESE.items():
        assert _placeholders(english) == _placeholders(japanese), english


@pytest.mark.parametrize(
    ("tags", "environment", "expected"),
    [
        (["ja-JP", "en-US"], {}, "ja"),
        (["en-US", "ja-JP"], {}, "en"),
        (["fr-FR", "ja"], {}, "ja"),
        (["fr-FR"], {}, "en"),
        ([], {}, "en"),
        (["en-US"], {"LASERGRBL_LANG": "ja_JP.UTF-8"}, "ja"),
        (["ja-JP"], {"LASERGRBL_LANG": "en"}, "en"),
        (["ja-JP"], {"LASERGRBL_LANG": "xx"}, "ja"),
    ],
)
def test_detects_language(tags, environment, expected) -> None:
    assert i18n.detect_language(tags, environment) == expected


def test_english_is_the_fallback() -> None:
    assert i18n.tr("Start job") == "Start job"
    assert i18n.tr("Completed in {duration}", duration="00:01:02") == "Completed in 00:01:02"
    assert i18n.tr("Text without a translation") == "Text without a translation"


def test_translates_and_formats_japanese() -> None:
    i18n.set_language("ja")
    assert i18n.tr("Start job") == "ジョブを開始"
    assert i18n.tr("Machine state: {state}", state="Idle") == "機械の状態: Idle"
    assert i18n.tr("Generated {count:,} G-code lines", count=12345) == "G-code を 12,345 行作成しました"
    assert i18n.tr("Text without a translation") == "Text without a translation"


def test_unknown_language_falls_back_to_english() -> None:
    i18n.set_language("xx")
    assert i18n.current_language() == "en"


def test_translates_core_module_errors() -> None:
    i18n.set_language("ja")
    settings = RasterSettings(width_mm=1000, height_mm=1000, pixels_per_mm=20, maximum_points=10)
    with pytest.raises(ValueError) as error:
        image_to_gcode(Path("unused.png"), settings)
    translated = i18n.tr_message(str(error.value))
    assert translated != str(error.value)
    assert "安全のための上限" in translated

    assert i18n.tr_message("No G-code is loaded.") == "G-code が読み込まれていません。"
    assert i18n.tr_message("error:20") == "error:20"
