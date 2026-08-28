# -*- coding: utf-8 -*-
"""Unit tests for report language helpers."""

import unittest

from src.report_language import (
    SUPPORTED_REPORT_LANGUAGES,
    display_metric,
    format_dashboard_number,
    format_money_amount,
    format_share_volume,
    get_bias_status_emoji,
    get_localized_stock_name,
    get_report_labels,
    get_sentiment_label,
    get_signal_level,
    infer_decision_type_from_advice,
    localize_action_window,
    localize_bias_status,
    localize_immediate_action,
    localize_index_display_name,
    localize_operation_advice,
    localize_position_size_text,
    localize_residual_zh_tokens,
    localize_time_sensitivity,
    localize_trend_prediction,
    localize_volume_status,
    normalize_report_language,
    uses_english_prompt_scaffolding,
)


class ReportLanguageTestCase(unittest.TestCase):
    def test_get_signal_level_handles_compound_sell_advice(self) -> None:
        signal_text, emoji, signal_tag = get_signal_level("卖出/观望", 60, "zh")

        self.assertEqual(signal_text, "卖出")
        self.assertEqual(emoji, "🔴")
        self.assertEqual(signal_tag, "sell")

    def test_get_signal_level_handles_compound_buy_advice_in_english(self) -> None:
        signal_text, emoji, signal_tag = get_signal_level("Buy / Watch", 40, "en")

        self.assertEqual(signal_text, "Buy")
        self.assertEqual(emoji, "🟢")
        self.assertEqual(signal_tag, "buy")

    def test_get_signal_level_score_fallback_uses_canonical_scale(self) -> None:
        self.assertEqual(get_signal_level("", 28, "zh"), ("减仓", "🟠", "reduce"))
        self.assertEqual(get_signal_level("", 38, "zh"), ("减仓", "🟠", "reduce"))
        self.assertEqual(get_signal_level("", 42, "zh"), ("观望", "⚪", "watch"))
        self.assertEqual(get_signal_level("", 55, "zh"), ("观望", "⚪", "watch"))
        self.assertEqual(get_signal_level("", 60, "zh"), ("买入", "🟢", "buy"))
        self.assertEqual(get_signal_level("", 66, "zh"), ("买入", "🟢", "buy"))
        self.assertEqual(get_signal_level("", 72, "zh"), ("买入", "🟢", "buy"))

    def test_get_localized_stock_name_replaces_placeholder_for_english(self) -> None:
        self.assertEqual(
            get_localized_stock_name("股票AAPL", "AAPL", "en"),
            "Unnamed Stock",
        )

    def test_get_sentiment_label_preserves_higher_band_thresholds(self) -> None:
        self.assertEqual(get_sentiment_label(80, "en"), "Very Bullish")
        self.assertEqual(get_sentiment_label(60, "en"), "Bullish")
        self.assertEqual(get_sentiment_label(40, "zh"), "中性")
        self.assertEqual(get_sentiment_label(20, "zh"), "悲观")

    def test_localize_trend_prediction_preserves_fine_grain_zh_states(self) -> None:
        self.assertEqual(localize_trend_prediction("多头排列", "zh"), "多头排列")
        self.assertEqual(localize_trend_prediction("弱势空头", "zh"), "弱势空头")

    def test_localize_trend_prediction_still_translates_english_input_for_zh(self) -> None:
        self.assertEqual(localize_trend_prediction("bullish", "zh"), "看多")
        self.assertEqual(localize_trend_prediction("very bearish", "zh"), "强烈看空")

    def test_bias_status_helpers_support_english_values(self) -> None:
        self.assertEqual(localize_bias_status("Safe", "en"), "Safe")
        self.assertEqual(localize_bias_status("警戒", "en"), "Caution")
        self.assertEqual(get_bias_status_emoji("Safe"), "✅")
        self.assertEqual(get_bias_status_emoji("Caution"), "⚠️")

    def test_infer_decision_type_from_advice_matches_chinese_phrases(self) -> None:
        self.assertEqual(infer_decision_type_from_advice("建议买入"), "buy")
        self.assertEqual(infer_decision_type_from_advice("建议持有"), "hold")
        self.assertEqual(infer_decision_type_from_advice("建议减仓"), "sell")
        self.assertEqual(infer_decision_type_from_advice("继续持有"), "hold")
        self.assertEqual(infer_decision_type_from_advice("建议洗盘观察"), "hold")
        self.assertEqual(infer_decision_type_from_advice("洗盘观察", default=""), "hold")
        self.assertEqual(infer_decision_type_from_advice("观察", default=""), "hold")
        self.assertEqual(infer_decision_type_from_advice("不建议买入"), "hold")
        self.assertEqual(
            infer_decision_type_from_advice("当前不跌破支撑位继续持有"),
            "hold",
        )
        self.assertEqual(
            infer_decision_type_from_advice("不破支撑后仍可持有"),
            "hold",
        )


class KoreanReportLanguageTestCase(unittest.TestCase):
    def test_korean_is_supported(self) -> None:
        self.assertIn("ko", SUPPORTED_REPORT_LANGUAGES)

    def test_normalize_korean_aliases(self) -> None:
        self.assertEqual(normalize_report_language("ko"), "ko")
        self.assertEqual(normalize_report_language("korean"), "ko")
        self.assertEqual(normalize_report_language("ko-KR"), "ko")
        self.assertEqual(normalize_report_language("kr"), "ko")

    def test_unknown_language_falls_back_to_default(self) -> None:
        self.assertEqual(normalize_report_language("fr"), "zh")
        self.assertEqual(normalize_report_language(None), "zh")

    def test_korean_labels_cover_full_english_key_set(self) -> None:
        ko_labels = get_report_labels("ko")
        en_labels = get_report_labels("en")
        self.assertEqual(set(ko_labels.keys()), set(en_labels.keys()))
        self.assertEqual(ko_labels["dashboard_title"], "결정 대시보드")
        self.assertEqual(ko_labels["risk_alerts_label"], "리스크 경보")

    def test_korean_sentiment_label_bands(self) -> None:
        self.assertEqual(get_sentiment_label(80, "ko"), "매우 낙관")
        self.assertEqual(get_sentiment_label(40, "ko"), "중립")
        self.assertEqual(get_sentiment_label(0, "ko"), "매우 비관")

    def test_korean_operation_advice_and_trend(self) -> None:
        self.assertEqual(localize_operation_advice("买入", "ko"), "매수")
        self.assertEqual(localize_operation_advice("strong sell", "ko"), "적극 매도")
        self.assertEqual(localize_trend_prediction("bullish", "ko"), "상승")

    def test_korean_localized_stock_name_placeholder(self) -> None:
        self.assertEqual(
            get_localized_stock_name("股票AAPL", "AAPL", "ko"),
            "미확인 종목",
        )

    def test_existing_languages_unchanged(self) -> None:
        self.assertEqual(get_sentiment_label(80, "en"), "Very Bullish")
        self.assertEqual(get_sentiment_label(40, "zh"), "中性")

    def test_korean_advice_canonicalizes_to_decision_type(self) -> None:
        self.assertEqual(infer_decision_type_from_advice("매수"), "buy")
        self.assertEqual(infer_decision_type_from_advice("매도"), "sell")
        self.assertEqual(infer_decision_type_from_advice("보유"), "hold")
        self.assertEqual(infer_decision_type_from_advice("관망"), "hold")

    def test_korean_advice_resolves_signal_level(self) -> None:
        self.assertEqual(get_signal_level("매수", 72, "ko"), ("매수", "🟢", "buy"))
        self.assertEqual(get_signal_level("매도", 30, "ko"), ("매도", "🔴", "sell"))

    def test_korean_values_canonicalize_back_for_other_languages(self) -> None:
        self.assertEqual(localize_trend_prediction("상승", "en"), "Bullish")
        self.assertEqual(localize_operation_advice("적극 매도", "zh"), "强烈卖出")


class ItalianReportLanguageTestCase(unittest.TestCase):
    def test_italian_is_supported(self) -> None:
        self.assertIn("it", SUPPORTED_REPORT_LANGUAGES)

    def test_normalize_italian_aliases(self) -> None:
        self.assertEqual(normalize_report_language("it"), "it")
        self.assertEqual(normalize_report_language("italian"), "it")
        self.assertEqual(normalize_report_language("italiano"), "it")
        self.assertEqual(normalize_report_language("it-IT"), "it")
        self.assertEqual(normalize_report_language("ita"), "it")

    def test_unknown_language_still_falls_back_to_default(self) -> None:
        self.assertEqual(normalize_report_language("fr"), "zh")
        self.assertEqual(normalize_report_language(None), "zh")

    def test_italian_labels_cover_full_english_key_set(self) -> None:
        it_labels = get_report_labels("it")
        en_labels = get_report_labels("en")
        self.assertEqual(set(it_labels.keys()), set(en_labels.keys()))
        self.assertEqual(it_labels["dashboard_title"], "Cruscotto decisionale")
        self.assertEqual(it_labels["risk_alerts_label"], "Allerte di rischio")

    def test_italian_sentiment_label_bands(self) -> None:
        self.assertEqual(get_sentiment_label(80, "it"), "Molto rialzista")
        self.assertEqual(get_sentiment_label(40, "it"), "Neutrale")
        self.assertEqual(get_sentiment_label(0, "it"), "Molto ribassista")

    def test_italian_operation_advice_and_trend(self) -> None:
        self.assertEqual(localize_operation_advice("买入", "it"), "Acquisto")
        self.assertEqual(localize_operation_advice("strong sell", "it"), "Vendita forte")
        self.assertEqual(localize_trend_prediction("bullish", "it"), "Rialzista")

    def test_italian_localized_stock_name_placeholder(self) -> None:
        self.assertEqual(
            get_localized_stock_name("股票AAPL", "AAPL", "it"),
            "Titolo da confermare",
        )

    def test_existing_languages_unchanged(self) -> None:
        self.assertEqual(get_sentiment_label(80, "en"), "Very Bullish")
        self.assertEqual(get_sentiment_label(40, "zh"), "中性")
        self.assertEqual(get_sentiment_label(80, "ko"), "매우 낙관")

    def test_italian_advice_canonicalizes_to_decision_type(self) -> None:
        self.assertEqual(infer_decision_type_from_advice("acquisto"), "buy")
        self.assertEqual(infer_decision_type_from_advice("vendi"), "sell")
        self.assertEqual(infer_decision_type_from_advice("mantieni"), "hold")
        self.assertEqual(infer_decision_type_from_advice("attendi"), "hold")

    def test_italian_advice_resolves_signal_level(self) -> None:
        self.assertEqual(get_signal_level("acquisto", 72, "it"), ("Acquisto", "🟢", "buy"))
        self.assertEqual(get_signal_level("vendi", 30, "it"), ("Vendi", "🔴", "sell"))

    def test_italian_values_canonicalize_back_for_other_languages(self) -> None:
        self.assertEqual(localize_trend_prediction("Rialzista", "en"), "Bullish")
        self.assertEqual(localize_operation_advice("Vendita forte", "zh"), "强烈卖出")

    def test_italian_uses_english_prompt_scaffolding(self) -> None:
        self.assertTrue(uses_english_prompt_scaffolding("it"))
        self.assertTrue(uses_english_prompt_scaffolding("ko"))
        self.assertTrue(uses_english_prompt_scaffolding("en"))
        self.assertFalse(uses_english_prompt_scaffolding("zh"))

    def test_italian_units_drop_chinese_share_and_currency_suffixes(self) -> None:
        self.assertNotIn("万股", format_share_volume(27100300, "it"))
        self.assertIn("mln di azioni", format_share_volume(27100300, "it"))
        self.assertNotIn("美元", format_money_amount(1e8, "USD", "it"))
        self.assertIn("USD", format_money_amount(1e8, "USD", "it"))
        self.assertEqual(format_share_volume(0, "zh"), "0 股")

    def test_italian_localizes_leftover_zh_enums_and_tokens(self) -> None:
        self.assertEqual(localize_position_size_text("3 成", "it"), "30%")
        self.assertEqual(localize_time_sensitivity("不急", "it"), "Non urgente")
        self.assertEqual(localize_bias_status("安全", "it"), "Sicuro")
        self.assertEqual(localize_volume_status("平量", "it"), "Volume stabile")
        self.assertEqual(localize_volume_status("縮量/Contrazione", "it"), "Contrazione")
        self.assertEqual(localize_action_window("盘后复盘", "it"), "Recap post-mercato")
        self.assertEqual(
            localize_immediate_action("无盘中动作", "it"),
            "Nessuna azione infragiornaliera",
        )
        self.assertNotIn(
            "利空",
            localize_residual_zh_tokens("Assenza di notizie 利空 strutturali", "it"),
        )
        self.assertEqual(localize_index_display_name("上证指数", "it"), "SSE Composite")

    def test_dashboard_metrics_hide_none_and_round_floats(self) -> None:
        self.assertEqual(display_metric(None), "N/A")
        self.assertEqual(display_metric("none"), "N/A")
        self.assertEqual(format_dashboard_number(721.1099853515625), "721.11")
        labels = get_report_labels("it")
        self.assertEqual(labels["label_separator"], ": ")
        self.assertEqual(labels["generated_at_label"], "Generato alle")


if __name__ == "__main__":
    unittest.main()
