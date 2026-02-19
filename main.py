import json
import os
import random
import shutil
import sys
import time
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Tuple

try:
    import requests
    from colorama import Fore, Style, init
except ImportError as exc:
    print(f"Dependency belum terpasang: {exc}")
    print("Install dulu: pip install -r requirements.txt")
    sys.exit(1)


class ConfigError(Exception):
    pass


class APIError(Exception):
    pass


THEME_PRIMARY = Fore.CYAN
THEME_SECONDARY = Fore.YELLOW
THEME_TEXT = Fore.WHITE
THEME_PRIMARY_BRIGHT = Fore.CYAN + Style.BRIGHT
THEME_SECONDARY_BRIGHT = Fore.YELLOW + Style.BRIGHT
THEME_TEXT_BRIGHT = Fore.WHITE + Style.BRIGHT
THEME_TEXT_DIM = Fore.WHITE + Style.DIM

COINGECKO_IDS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "ltc": "litecoin",
    "doge": "dogecoin",
    "trx": "tron",
    "bch": "bitcoin-cash",
    "xrp": "ripple",
    "usdt": "tether",
    "uni": "uniswap",
    "sushi": "sushi",
    "xlm": "stellar",
    "etc": "ethereum-classic",
    "bnb": "binancecoin",
    "dot": "polkadot",
    "ada": "cardano",
    "shib": "shiba-inu",
    "matic": "matic-network",
    "optim": "optimism",
}


def default_config() -> Dict[str, Any]:
    return {
        "api": {
            "base_url": "https://wolfbet.com/api/v1",
            "token": "PASTE_WOLFBET_API_TOKEN",
            "timeout_seconds": 20,
            "retry_count": 3,
            "rate_limit_wait_seconds": 60,
        },
        "simple": {
            "enabled": "OFF",
            "currency": "trx",
            "hilo_fixed": "LOW",
            "hilo_random": "OFF",
            "bet_amount": 0.00000001,
            "multiplier": 1.98,
            "chance_random": "OFF",
            "chance_random_min": 40.0,
            "chance_random_max": 60.0,
            "chance_random_precision": 2,
            "system": "martingale",
            "preset_prompt": "ON",
            "reset_if_win": "ON",
            "reset_if_loss": "OFF",
            "increase_after_win_percent": 0,
            "increase_after_loss_percent": 100,
            "max_bet_stop": 0,
            "balance_stop": 0,
            "profit_stop": 0,
            "stop_loss": 0,
            "max_bets": 0,
            "bet_interval_ms": 1000,
            "replay_on_take_profit": "OFF",
            "replay_on_stop_loss": "OFF",
            "replay_after_sec": 5,
            "replay_count": 0,
        },
        "bot": {
            "currency": "trx",
            "rule": "under",
            "base_amount": 0.0001,
            "bet_value": 49.99,
            "multiplier": 1.98,
            "auto_multiplier": "OFF",
            "sync_mode": "auto",
            "sync_fallback_mode": "lock_multiplier",
            "multiplier_precision": 4,
            "bet_value_precision": 2,
            "save_synced_pair_to_config": "ON",
            "last_synced_multiplier": 0,
            "last_synced_bet_value": 0,
            "delay_seconds": 1.0,
            "max_bets": 0,
            "target_profit": 0,
            "stop_loss": 0,
            "stop_on_balance_below": 0,
            "max_amount": 0,
            "max_consecutive_losses": 0,
            "max_consecutive_wins": 0,
            "continue_on_api_error": "ON",
            "max_api_errors": 5,
            "refresh_server_seed_every": 0,
            "refresh_client_seed_every": 0,
        },
        "strategy": {
            "switch_rule_on_win": "OFF",
            "switch_rule_on_loss": "OFF",
            "preset": {
                "enabled": "OFF",
                "use": {
                    "martingale": "OFF",
                    "fibonacci": "OFF",
                    "paroli": "OFF",
                    "anti_martingale": "OFF",
                    "dalembert": "OFF",
                    "flat": "OFF",
                    "mining": "OFF",
                    "mining_v2": "OFF",
                    "pro_safe": "OFF",
                    "pro_recovery": "OFF",
                },
                "martingale_multiplier": 2.0,
                "fibonacci_unit": 1.0,
                "fibonacci_step_back_on_win": 2,
                "paroli_multiplier": 2.0,
                "paroli_max_win_streak": 3,
                "dalembert_step": 1.0,
                "long_run_loss_multiplier": 1.08,
                "long_run_max_steps": 8,
                "long_run_recovery_steps_on_win": 2,
                "long_run_max_scale": 2.0,
                "long_run_shield_after_losses": 5,
                "long_run_shield_rounds": 2,
                "mining_v2_loss_multiplier": 1.03,
                "mining_v2_max_steps": 6,
                "mining_v2_recovery_steps_on_win": 3,
                "mining_v2_max_scale": 1.50,
                "mining_v2_cooldown_trigger_losses": 4,
                "mining_v2_cooldown_rounds": 2,
                "pro_safe_loss_multiplier": 1.02,
                "pro_safe_max_steps": 5,
                "pro_safe_recovery_steps_on_win": 2,
                "pro_safe_max_scale": 1.25,
                "pro_recovery_loss_multiplier": 1.06,
                "pro_recovery_max_steps": 6,
                "pro_recovery_recovery_steps_on_win": 1,
                "pro_recovery_max_scale": 2.0,
                "pro_recovery_cooldown_trigger_losses": 4,
                "pro_recovery_cooldown_rounds": 2,
                "pro_scalper_win_multiplier": 1.35,
                "pro_scalper_max_win_streak": 3,
                "premium_guard_loss_multiplier": 1.04,
                "premium_guard_max_steps": 5,
                "premium_guard_max_scale": 1.40,
                "premium_guard_risk_percent": 0.03,
                "premium_guard_cooldown_trigger_losses": 4,
                "premium_guard_cooldown_rounds": 2,
                "premium_compound_loss_multiplier": 1.03,
                "premium_compound_max_steps": 5,
                "premium_compound_recovery_steps_on_win": 2,
                "premium_compound_max_scale": 1.60,
                "premium_compound_profit_boost_percent": 15.0,
                "premium_daily_target_percent": 10,
                "premium_stop_loss_percent": 5,
                "premium_risk_percent": 0.05,
                "premium_max_risk_percent": 0.25,
                "premium_loss_multiplier": 1.06,
                "premium_max_steps": 5,
                "premium_recovery_steps_on_win": 2,
                "premium_max_scale": 1.35,
                "premium_cooldown_trigger_losses": 4,
                "premium_cooldown_rounds": 2,
            },
            "on_win": {
                "reset_to_base": "ON",
                "amount_multiplier": 1.0,
                "amount_addition": 0.0,
            },
            "on_loss": {
                "reset_to_base": "OFF",
                "amount_multiplier": 2.0,
                "amount_addition": 0.0,
            },
        },
        "display": {
            "show_timestamp": "ON",
            "show_balance_each_bet": "ON",
            "history_style": "mining",
            "history_header_every": 20,
            "history_width": 0,
            "amount_display_precision": 8,
            "profit_display_precision": 8,
            "balance_display_precision": 8,
            "coin_decimal_places": 8,
            "sticky_stats_footer": "ON",
            "balance_sync_mode": "hybrid",
            "balance_refresh_every": 20,
            "show_idr_value": "OFF",
            "idr_refresh_seconds": 30,
        },
    }


def default_user_config_template() -> Dict[str, Any]:
    defaults = default_config()
    return {
        "api": defaults["api"],
        "simple": {
            **defaults["simple"],
            "enabled": "ON",
        },
        "display": {
            "history_style": "mining",
            "sticky_stats_footer": "ON",
            "coin_decimal_places": 8,
            "balance_sync_mode": "hybrid",
            "balance_refresh_every": 20,
            "show_idr_value": "OFF",
            "idr_refresh_seconds": 30,
        },
    }


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def to_decimal(value: Any, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ConfigError(f"Nilai tidak valid untuk '{field_name}': {value}") from exc


def parse_toggle(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False

    text = str(value).strip().upper()
    if text in {"ON", "TRUE", "YES", "Y", "1"}:
        return True
    if text in {"OFF", "FALSE", "NO", "N", "0"}:
        return False

    raise ConfigError(f"Nilai '{field_name}' harus ON/OFF.")


SUPPORTED_PRESETS = (
    "martingale",
    "fibonacci",
    "paroli",
    "anti_martingale",
    "dalembert",
    "flat",
    "mining",
    "mining_v2",
    "pro_safe",
    "pro_recovery",
)

PRESET_ALIAS_MAP = {
    "long_run_guard": "mining",
    "anti_losstrack": "mining",
    "pro_scalper": "pro_recovery",
    "premium_guard": "pro_safe",
    "premium_compound": "mining_v2",
    "premium": "pro_recovery",
}

SIMPLE_SYSTEM_ALIAS_MAP = {
    "custom": "",
    "manual": "",
    "off": "",
    "none": "",
    "martingale": "martingale",
    "fibonacci": "fibonacci",
    "paroli": "paroli",
    "anti_martingale": "anti_martingale",
    "anti-martingale": "anti_martingale",
    "dalembert": "dalembert",
    "d'alembert": "dalembert",
    "flat": "flat",
    "mining": "mining",
    "long_run_guard": "mining",
    "anti_losstrack": "mining",
    "mining_v2": "mining_v2",
    "pro_safe": "pro_safe",
    "pro-safe": "pro_safe",
    "pro_recovery": "pro_recovery",
    "pro-recovery": "pro_recovery",
    "pro_scalper": "pro_recovery",
    "pro-scalper": "pro_recovery",
    "premium_guard": "pro_safe",
    "premium-guard": "pro_safe",
    "premium_compound": "mining_v2",
    "premium-compound": "mining_v2",
    "premium": "pro_recovery",
}


def canonical_preset_name(name: str) -> str:
    return PRESET_ALIAS_MAP.get(name, name)


def to_on_off(value: bool) -> str:
    return "ON" if value else "OFF"


def normalize_simple_system(value: Any, field_name: str = "simple.system") -> str:
    key = str(value).strip().lower()
    if key in SIMPLE_SYSTEM_ALIAS_MAP:
        return SIMPLE_SYSTEM_ALIAS_MAP[key]
    supported = ", ".join(("custom",) + SUPPORTED_PRESETS)
    raise ConfigError(f"{field_name} '{value}' tidak didukung. Pilihan: {supported}")


def normalize_hilo_fixed(value: Any, field_name: str = "simple.hilo_fixed") -> str:
    key = str(value).strip().lower()
    if key in {"low", "lo", "under"}:
        return "under"
    if key in {"high", "hi", "over"}:
        return "over"
    raise ConfigError(f"{field_name} harus HI/LOW (atau over/under).")


def compute_bet_value_from_multiplier_backend(multiplier: Decimal, rule: str, precision: int) -> Decimal:
    if multiplier <= Decimal("1"):
        raise ConfigError("simple.multiplier harus > 1.")
    chance = Decimal("99") / multiplier
    if rule == "under":
        bet_value = chance
    else:
        bet_value = Decimal("99.99") - chance

    step = Decimal("1").scaleb(-precision)
    bet_value = bet_value.quantize(step, rounding=ROUND_HALF_UP)
    if bet_value <= Decimal("0") or bet_value >= Decimal("99.99"):
        raise ConfigError("Hasil sinkronisasi chance dari simple.multiplier di luar batas valid.")
    return bet_value


def apply_simple_settings(cfg: Dict[str, Any]) -> None:
    simple_cfg = cfg.get("simple", {})
    if simple_cfg is None:
        return
    if not isinstance(simple_cfg, dict):
        raise ConfigError("simple harus object JSON.")

    simple_enabled = parse_toggle(simple_cfg.get("enabled", "OFF"), "simple.enabled")
    if not simple_enabled:
        return

    bot_cfg = cfg["bot"]
    strategy_cfg = cfg["strategy"]
    preset_cfg = strategy_cfg.get("preset", {})
    preset_use = preset_cfg.get("use", {})
    on_win_cfg = strategy_cfg.get("on_win", {})
    on_loss_cfg = strategy_cfg.get("on_loss", {})

    if not isinstance(preset_use, dict):
        raise ConfigError("strategy.preset.use harus object JSON.")

    currency = str(simple_cfg.get("currency", bot_cfg.get("currency", "trx"))).strip().lower()
    legacy_rule = str(simple_cfg.get("rule", bot_cfg.get("rule", "under"))).strip().lower()
    fixed_rule = normalize_hilo_fixed(simple_cfg.get("hilo_fixed", legacy_rule))

    bet_amount = to_decimal(simple_cfg.get("bet_amount", bot_cfg.get("base_amount", 0)), "simple.bet_amount")
    multiplier = to_decimal(simple_cfg.get("multiplier", bot_cfg.get("multiplier", 0)), "simple.multiplier")
    bet_interval_ms = to_decimal(simple_cfg.get("bet_interval_ms", 1000), "simple.bet_interval_ms")
    if bet_interval_ms < 0:
        raise ConfigError("simple.bet_interval_ms tidak boleh negatif.")

    if "hilo_random" in simple_cfg:
        hilo_random = parse_toggle(simple_cfg.get("hilo_random", "OFF"), "simple.hilo_random")
    else:
        legacy_hilo_mode = str(simple_cfg.get("hilo_mode", "fixed")).strip().lower()
        if legacy_hilo_mode not in {"fixed", "random"}:
            raise ConfigError("simple.hilo_mode harus 'fixed' atau 'random'.")
        hilo_random = legacy_hilo_mode == "random"

    chance_random = parse_toggle(simple_cfg.get("chance_random", "OFF"), "simple.chance_random")
    chance_random_min = to_decimal(simple_cfg.get("chance_random_min", 40.0), "simple.chance_random_min")
    chance_random_max = to_decimal(simple_cfg.get("chance_random_max", 60.0), "simple.chance_random_max")
    chance_random_precision = int(simple_cfg.get("chance_random_precision", 2))
    if chance_random_min <= 0 or chance_random_min >= Decimal("99.99"):
        raise ConfigError("simple.chance_random_min harus > 0 dan < 99.99.")
    if chance_random_max <= 0 or chance_random_max >= Decimal("99.99"):
        raise ConfigError("simple.chance_random_max harus > 0 dan < 99.99.")
    if chance_random_min > chance_random_max:
        raise ConfigError("simple.chance_random_min tidak boleh lebih besar dari chance_random_max.")
    if chance_random_precision < 0 or chance_random_precision > 8:
        raise ConfigError("simple.chance_random_precision harus 0-8.")

    increase_win_pct = to_decimal(
        simple_cfg.get("increase_after_win_percent", 0), "simple.increase_after_win_percent"
    )
    increase_loss_pct = to_decimal(
        simple_cfg.get("increase_after_loss_percent", 100), "simple.increase_after_loss_percent"
    )
    if increase_win_pct < 0:
        raise ConfigError("simple.increase_after_win_percent tidak boleh negatif.")
    if increase_loss_pct < 0:
        raise ConfigError("simple.increase_after_loss_percent tidak boleh negatif.")

    reset_if_win = parse_toggle(simple_cfg.get("reset_if_win", "ON"), "simple.reset_if_win")
    reset_if_loss = parse_toggle(simple_cfg.get("reset_if_loss", "OFF"), "simple.reset_if_loss")
    preset_prompt = parse_toggle(simple_cfg.get("preset_prompt", "ON"), "simple.preset_prompt")
    replay_on_take_profit = parse_toggle(
        simple_cfg.get("replay_on_take_profit", "OFF"), "simple.replay_on_take_profit"
    )
    replay_on_stop_loss = parse_toggle(
        simple_cfg.get("replay_on_stop_loss", "OFF"), "simple.replay_on_stop_loss"
    )
    replay_after_sec = to_decimal(simple_cfg.get("replay_after_sec", 5), "simple.replay_after_sec")
    replay_count = int(simple_cfg.get("replay_count", 0))
    if replay_after_sec < 0:
        raise ConfigError("simple.replay_after_sec tidak boleh negatif.")
    if replay_count < 0:
        raise ConfigError("simple.replay_count tidak boleh negatif.")

    selected_system = normalize_simple_system(simple_cfg.get("system", "martingale"))
    bet_value_precision = int(bot_cfg.get("bet_value_precision", 2))
    if bet_value_precision < 0 or bet_value_precision > 8:
        raise ConfigError("bot.bet_value_precision harus 0-8.")
    calculated_bet_value = compute_bet_value_from_multiplier_backend(multiplier, fixed_rule, bet_value_precision)

    bot_cfg["currency"] = currency
    bot_cfg["rule"] = fixed_rule
    bot_cfg["base_amount"] = float(bet_amount)
    bot_cfg["bet_value"] = float(calculated_bet_value)
    bot_cfg["multiplier"] = float(multiplier)
    bot_cfg["auto_multiplier"] = "OFF"
    bot_cfg["sync_mode"] = "lock_bet_value" if chance_random else "lock_multiplier"
    bot_cfg["sync_fallback_mode"] = bot_cfg["sync_mode"]
    bot_cfg["delay_seconds"] = float(bet_interval_ms / Decimal("1000"))
    bot_cfg["max_amount"] = float(to_decimal(simple_cfg.get("max_bet_stop", 0), "simple.max_bet_stop"))
    bot_cfg["stop_on_balance_below"] = float(to_decimal(simple_cfg.get("balance_stop", 0), "simple.balance_stop"))
    bot_cfg["target_profit"] = float(to_decimal(simple_cfg.get("profit_stop", 0), "simple.profit_stop"))
    bot_cfg["stop_loss"] = float(to_decimal(simple_cfg.get("stop_loss", 0), "simple.stop_loss"))
    bot_cfg["max_bets"] = int(simple_cfg.get("max_bets", 0))
    bot_cfg["save_synced_pair_to_config"] = "ON"
    bot_cfg["last_synced_multiplier"] = float(multiplier)
    bot_cfg["last_synced_bet_value"] = float(calculated_bet_value)

    strategy_cfg["switch_rule_on_win"] = "OFF"
    strategy_cfg["switch_rule_on_loss"] = "OFF"
    on_win_cfg["reset_to_base"] = to_on_off(reset_if_win)
    on_loss_cfg["reset_to_base"] = to_on_off(reset_if_loss)
    on_win_cfg["amount_multiplier"] = float(Decimal("1") + (increase_win_pct / Decimal("100")))
    on_win_cfg["amount_addition"] = 0.0
    on_loss_cfg["amount_multiplier"] = float(Decimal("1") + (increase_loss_pct / Decimal("100")))
    on_loss_cfg["amount_addition"] = 0.0

    for preset_name in list(preset_use.keys()):
        preset_use[preset_name] = "OFF"
    for preset_name in SUPPORTED_PRESETS:
        preset_use[preset_name] = "OFF"

    if selected_system:
        preset_use[selected_system] = "ON"
        preset_cfg["enabled"] = "ON"
    else:
        preset_cfg["enabled"] = "OFF"

    strategy_cfg["on_win"] = on_win_cfg
    strategy_cfg["on_loss"] = on_loss_cfg
    preset_cfg["use"] = preset_use
    strategy_cfg["preset"] = preset_cfg

    simple_cfg["hilo_fixed"] = "LOW" if fixed_rule == "under" else "HI"
    simple_cfg["hilo_random"] = to_on_off(hilo_random)
    simple_cfg["chance_random"] = to_on_off(chance_random)
    simple_cfg["chance_random_min"] = float(chance_random_min)
    simple_cfg["chance_random_max"] = float(chance_random_max)
    simple_cfg["chance_random_precision"] = chance_random_precision
    simple_cfg["preset_prompt"] = to_on_off(preset_prompt)
    simple_cfg["replay_on_take_profit"] = to_on_off(replay_on_take_profit)
    simple_cfg["replay_on_stop_loss"] = to_on_off(replay_on_stop_loss)
    simple_cfg["replay_after_sec"] = float(replay_after_sec)
    simple_cfg["replay_count"] = replay_count
    simple_cfg.pop("rule", None)
    simple_cfg.pop("hilo_mode", None)
    simple_cfg.pop("save_synced_pair_to_config", None)
    simple_cfg.pop("last_synced_multiplier", None)
    simple_cfg.pop("last_synced_chance", None)
    simple_cfg.pop("chance", None)
    simple_cfg.pop("auto_sync_pair", None)
    simple_cfg.pop("sync_mode", None)


def resolve_selected_preset(preset_cfg: Dict[str, Any], field_prefix: str = "strategy.preset") -> str:
    use_cfg = preset_cfg.get("use", {})
    if use_cfg is None:
        use_cfg = {}
    if not isinstance(use_cfg, dict):
        raise ConfigError(f"{field_prefix}.use harus object JSON.")

    selected_raw = []
    selected_canonical = set()
    for raw_key, raw_value in use_cfg.items():
        key = str(raw_key).strip().lower()
        canonical = canonical_preset_name(key)
        if key in SUPPORTED_PRESETS:
            effective = key
        elif canonical in SUPPORTED_PRESETS:
            effective = canonical
        else:
            supported = ", ".join(SUPPORTED_PRESETS)
            raise ConfigError(f"{field_prefix}.use.{raw_key} tidak dikenali. Pilihan: {supported}")

        if parse_toggle(raw_value, f"{field_prefix}.use.{raw_key}"):
            selected_raw.append(key)
            selected_canonical.add(effective)

    if len(selected_canonical) > 1:
        selected_list = ", ".join(sorted(selected_raw))
        raise ConfigError(f"Hanya boleh satu preset aktif (ON). Saat ini ON: {selected_list}")

    if len(selected_canonical) == 1:
        return next(iter(selected_canonical))

    legacy_name = str(preset_cfg.get("name", "")).strip().lower()
    if legacy_name:
        canonical = canonical_preset_name(legacy_name)
        if legacy_name in SUPPORTED_PRESETS:
            return legacy_name
        if canonical in SUPPORTED_PRESETS:
            return canonical
        else:
            supported = ", ".join(SUPPORTED_PRESETS)
            raise ConfigError(f"{field_prefix}.name '{legacy_name}' tidak didukung. Pilihan: {supported}")

    return ""


def format_decimal(value: Decimal, places: int = 10) -> str:
    quant = Decimal("1." + ("0" * places))
    text = format(value.quantize(quant, rounding=ROUND_DOWN), "f")
    text = text.rstrip("0").rstrip(".")
    return text if text else "0"


def quantize_places(value: Decimal, places: int) -> Decimal:
    step = Decimal("1").scaleb(-places)
    return value.quantize(step, rounding=ROUND_DOWN)


def quantize_places_half_up(value: Decimal, places: int) -> Decimal:
    step = Decimal("1").scaleb(-places)
    return value.quantize(step, rounding=ROUND_HALF_UP)


def decimal_to_plain(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        return "0"
    return text


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_banner() -> None:
    clear_screen()
    lines = [
        " _   _ _   _ ____    _    _   _ _____  _    ____      _    ____   ___ _____ ",
        "| \\ | | | | / ___|  / \\  | \\ | |_   _|/ \\  |  _ \\    / \\  | __ ) / _ \\_   _|",
        "|  \\| | | | \\___ \\ / _ \\ |  \\| | | | / _ \\ | |_) |  / _ \\ |  _ \\| | | || |  ",
        "| |\\  | |_| |___) / ___ \\| |\\  | | |/ ___ \\|  _ <  / ___ \\| |_) | |_| || |  ",
        "|_| \\_|\\___/|____/_/   \\_\\_| \\_| |_/_/   \\_\\_| \\_\\/_/   \\_\\____/ \\___/ |_|  ",
    ]
    accent = THEME_PRIMARY_BRIGHT
    for line in lines:
        print(accent + line)
    print(THEME_TEXT_DIM + " " + "-" * 83)
    print(THEME_TEXT_BRIGHT + " for wolfbet")
    print(THEME_SECONDARY_BRIGHT + " developer cipow")
    print(THEME_TEXT_DIM + " " + "-" * 83)
    print("")


class WolfbetClient:
    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.base_url = str(cfg["api"]["base_url"]).rstrip("/")
        token = str(cfg["api"]["token"]).strip()
        if not token.lower().startswith("bearer "):
            token = f"Bearer {token}"

        self.timeout = float(cfg["api"]["timeout_seconds"])
        self.retry_count = int(cfg["api"]["retry_count"])
        self.rate_limit_wait_seconds = int(cfg["api"]["rate_limit_wait_seconds"])
        self.runtime_warn_logger: Callable[[str], None] | None = None

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": token,
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "NUSANTARA-BOT/1.0",
            }
        )

    def set_runtime_warn_logger(self, logger: Callable[[str], None] | None) -> None:
        self.runtime_warn_logger = logger

    def _warn(self, message: str) -> None:
        if self.runtime_warn_logger is not None:
            self.runtime_warn_logger(message)
            return
        print(THEME_SECONDARY + message)

    def _safe_error_body(self, response: requests.Response) -> str:
        try:
            body = response.json()
            if isinstance(body, dict):
                if "message" in body:
                    return str(body["message"])
                if "error" in body:
                    return str(body["error"])
            return json.dumps(body, ensure_ascii=False)[:400]
        except ValueError:
            return (response.text or "Unknown error")[:400]

    def _parse_json(self, response: requests.Response) -> Dict[str, Any]:
        try:
            parsed = response.json()
            if isinstance(parsed, dict):
                return parsed
            return {"data": parsed}
        except ValueError as exc:
            raise APIError("Response API bukan JSON valid.") from exc

    def _request(
        self,
        method: str,
        path: str,
        payload: Dict[str, Any] | None = None,
        raw_json_payload: str | None = None,
    ) -> Tuple[Dict[str, Any], requests.Response]:
        url = f"{self.base_url}{path}"
        for attempt in range(self.retry_count + 1):
            try:
                request_kwargs: Dict[str, Any] = {"method": method, "url": url, "timeout": self.timeout}
                if raw_json_payload is not None:
                    request_kwargs["data"] = raw_json_payload
                else:
                    request_kwargs["json"] = payload
                response = self.session.request(**request_kwargs)
            except requests.RequestException as exc:
                if attempt >= self.retry_count:
                    raise APIError(f"Gagal konek ke API: {exc}") from exc
                wait_time = min(2 + attempt, 10)
                self._warn(f"[WARN] Network error, retry dalam {wait_time}s ...")
                time.sleep(wait_time)
                continue

            remaining = response.headers.get("x-ratelimit-remaining")
            if response.status_code == 429:
                if attempt >= self.retry_count:
                    raise APIError("Rate limit kena (429) dan retry habis.")
                self._warn(f"[WARN] Rate limit tercapai. Tunggu {self.rate_limit_wait_seconds}s lalu retry ...")
                time.sleep(self.rate_limit_wait_seconds)
                continue

            if not response.ok:
                detail = self._safe_error_body(response)
                raise APIError(f"HTTP {response.status_code}: {detail}")

            parsed = self._parse_json(response)

            if remaining is not None:
                try:
                    if int(remaining) <= 0:
                        self._warn(f"[WARN] x-ratelimit-remaining=0, cooldown {self.rate_limit_wait_seconds}s ...")
                        time.sleep(self.rate_limit_wait_seconds)
                except ValueError:
                    pass

            return parsed, response

        raise APIError("Request gagal setelah seluruh retry.")

    def get_balances(self) -> Dict[str, Any]:
        data, _ = self._request("GET", "/user/balances")
        return data

    def place_dice_bet(
        self,
        currency: str,
        amount: Decimal,
        rule: str,
        multiplier: Decimal,
        bet_value: Decimal,
    ) -> Dict[str, Any]:
        payload_json = (
            "{"
            f"\"currency\":\"{currency.lower()}\","
            "\"game\":\"dice\","
            f"\"amount\":{decimal_to_plain(amount)},"
            f"\"rule\":\"{rule}\","
            f"\"multiplier\":{decimal_to_plain(multiplier)},"
            f"\"bet_value\":{decimal_to_plain(bet_value)}"
            "}"
        )
        data, _ = self._request("POST", "/bet/place", raw_json_payload=payload_json)
        return data

    def refresh_client_seed(self, client_seed: str) -> Dict[str, Any]:
        data, _ = self._request("POST", "/user/seed/refresh", {"client_seed": client_seed})
        return data

    def refresh_server_seed(self) -> Dict[str, Any]:
        data, _ = self._request("GET", "/game/seed/refresh")
        return data


class DiceBot:
    def __init__(self, cfg: Dict[str, Any], client: WolfbetClient) -> None:
        self.cfg = cfg
        self.client = client

        bot = cfg["bot"]
        self.currency = str(bot["currency"]).lower()
        self.rule = str(bot["rule"]).lower()
        self.base_amount = to_decimal(bot["base_amount"], "bot.base_amount")
        self.current_amount = self.base_amount
        self.bet_value = to_decimal(bot["bet_value"], "bot.bet_value")
        self.auto_multiplier = parse_toggle(bot.get("auto_multiplier", "OFF"), "bot.auto_multiplier")
        self.multiplier = to_decimal(bot["multiplier"], "bot.multiplier")
        self.sync_mode = str(bot.get("sync_mode", "auto")).lower()
        self.sync_fallback_mode = str(bot.get("sync_fallback_mode", "lock_multiplier")).lower()
        self.multiplier_precision = int(bot.get("multiplier_precision", 4))
        self.bet_value_precision = int(bot.get("bet_value_precision", 2))
        self.save_synced_pair_to_config = parse_toggle(
            bot.get("save_synced_pair_to_config", "ON"), "bot.save_synced_pair_to_config"
        )
        self.last_synced_multiplier = to_decimal(
            bot.get("last_synced_multiplier", 0), "bot.last_synced_multiplier"
        )
        self.last_synced_bet_value = to_decimal(
            bot.get("last_synced_bet_value", 0), "bot.last_synced_bet_value"
        )
        self.input_multiplier = self.multiplier
        self.input_bet_value = self.bet_value

        if self.sync_mode not in {"lock_multiplier", "lock_bet_value", "none", "auto"}:
            raise ConfigError("bot.sync_mode harus salah satu: auto, lock_multiplier, lock_bet_value, none.")
        if self.sync_fallback_mode not in {"lock_multiplier", "lock_bet_value", "none"}:
            raise ConfigError("bot.sync_fallback_mode harus salah satu: lock_multiplier, lock_bet_value, none.")
        if self.multiplier_precision < 0 or self.multiplier_precision > 8:
            raise ConfigError("bot.multiplier_precision harus 0-8.")
        if self.bet_value_precision < 0 or self.bet_value_precision > 8:
            raise ConfigError("bot.bet_value_precision harus 0-8.")

        self.delay_seconds = float(bot["delay_seconds"])
        self.max_bets = int(bot["max_bets"])
        self.target_profit = to_decimal(bot["target_profit"], "bot.target_profit")
        self.stop_loss = to_decimal(bot["stop_loss"], "bot.stop_loss")
        self.stop_on_balance_below = to_decimal(bot["stop_on_balance_below"], "bot.stop_on_balance_below")
        self.max_amount = to_decimal(bot["max_amount"], "bot.max_amount")
        self.max_consecutive_losses = int(bot["max_consecutive_losses"])
        self.max_consecutive_wins = int(bot["max_consecutive_wins"])
        self.continue_on_api_error = parse_toggle(bot.get("continue_on_api_error", "ON"), "bot.continue_on_api_error")
        self.max_api_errors = int(bot["max_api_errors"])
        self.refresh_server_seed_every = int(bot["refresh_server_seed_every"])
        self.refresh_client_seed_every = int(bot["refresh_client_seed_every"])

        self.show_timestamp = parse_toggle(cfg["display"].get("show_timestamp", "ON"), "display.show_timestamp")
        self.show_balance_each_bet = parse_toggle(
            cfg["display"].get("show_balance_each_bet", "ON"), "display.show_balance_each_bet"
        )
        self.history_style = str(cfg["display"].get("history_style", "mining")).lower()
        self.history_header_every = int(cfg["display"].get("history_header_every", 20))
        self.history_width = int(cfg["display"].get("history_width", 0))
        self.coin_decimal_places = int(cfg["display"].get("coin_decimal_places", 8))
        self.amount_display_precision = int(cfg["display"].get("amount_display_precision", self.coin_decimal_places))
        self.profit_display_precision = int(cfg["display"].get("profit_display_precision", self.coin_decimal_places))
        self.balance_display_precision = int(cfg["display"].get("balance_display_precision", self.coin_decimal_places))
        self.sticky_stats_footer = parse_toggle(
            cfg["display"].get("sticky_stats_footer", "ON"), "display.sticky_stats_footer"
        )
        self.balance_sync_mode = str(cfg["display"].get("balance_sync_mode", "hybrid")).lower()
        self.balance_refresh_every = int(cfg["display"].get("balance_refresh_every", 20))
        self.show_idr_value = parse_toggle(cfg["display"].get("show_idr_value", "OFF"), "display.show_idr_value")
        self.idr_refresh_seconds = int(cfg["display"].get("idr_refresh_seconds", 30))

        if self.history_style not in {"mining", "classic"}:
            raise ConfigError("display.history_style harus 'mining' atau 'classic'.")
        if self.history_header_every < 0:
            raise ConfigError("display.history_header_every tidak boleh negatif.")
        if self.history_width < 0:
            raise ConfigError("display.history_width tidak boleh negatif.")
        if self.amount_display_precision < 0 or self.amount_display_precision > 8:
            raise ConfigError("display.amount_display_precision harus 0-8.")
        if self.profit_display_precision < 0 or self.profit_display_precision > 8:
            raise ConfigError("display.profit_display_precision harus 0-8.")
        if self.balance_display_precision < 0 or self.balance_display_precision > 8:
            raise ConfigError("display.balance_display_precision harus 0-8.")
        if self.coin_decimal_places < 0 or self.coin_decimal_places > 8:
            raise ConfigError("display.coin_decimal_places harus 0-8.")
        if self.amount_display_precision > self.coin_decimal_places:
            self.amount_display_precision = self.coin_decimal_places
        if self.profit_display_precision > self.coin_decimal_places:
            self.profit_display_precision = self.coin_decimal_places
        if self.balance_display_precision > self.coin_decimal_places:
            self.balance_display_precision = self.coin_decimal_places
        if self.balance_sync_mode not in {"hybrid", "api", "estimated"}:
            raise ConfigError("display.balance_sync_mode harus 'hybrid', 'api', atau 'estimated'.")
        if self.balance_refresh_every < 0:
            raise ConfigError("display.balance_refresh_every tidak boleh negatif.")
        if self.idr_refresh_seconds < 0:
            raise ConfigError("display.idr_refresh_seconds tidak boleh negatif.")

        self.currency_display = self.currency.upper()
        self.sticky_footer_enabled = self.sticky_stats_footer and sys.stdout.isatty()
        self._sticky_region_active = False
        self._sticky_region_size: Tuple[int, int] = (0, 0)
        self.idr_coin_id = COINGECKO_IDS.get(self.currency)
        self.idr_price = Decimal("0")
        self.idr_last_update_ts = 0.0
        self.idr_last_update_at = "--:--:--"
        self.idr_status = "OFF"
        self.idr_error_notified = False
        if self.show_idr_value:
            if self.idr_coin_id is None:
                self.idr_status = "UNSUPPORTED"
                self.show_idr_value = False
            else:
                self.idr_status = "INIT"
        simple_cfg = cfg.get("simple", {})
        if simple_cfg is None:
            simple_cfg = {}
        self.simple_mode_enabled = parse_toggle(simple_cfg.get("enabled", "OFF"), "simple.enabled")
        self.simple_system = normalize_simple_system(simple_cfg.get("system", "custom")) if self.simple_mode_enabled else ""
        legacy_rule = str(simple_cfg.get("rule", self.rule)).lower()
        self.simple_fixed_rule = normalize_hilo_fixed(simple_cfg.get("hilo_fixed", legacy_rule))
        if "hilo_random" in simple_cfg:
            self.simple_hilo_random = parse_toggle(simple_cfg.get("hilo_random", "OFF"), "simple.hilo_random")
        else:
            self.simple_hilo_random = str(simple_cfg.get("hilo_mode", "fixed")).lower() == "random"
        self.simple_chance_random_enabled = parse_toggle(
            simple_cfg.get("chance_random", "OFF"), "simple.chance_random"
        )
        self.simple_chance_random_min = to_decimal(
            simple_cfg.get("chance_random_min", 40.0), "simple.chance_random_min"
        )
        self.simple_chance_random_max = to_decimal(
            simple_cfg.get("chance_random_max", 60.0), "simple.chance_random_max"
        )
        self.simple_chance_random_precision = int(simple_cfg.get("chance_random_precision", 2))
        if self.simple_chance_random_min <= 0 or self.simple_chance_random_min >= Decimal("99.99"):
            raise ConfigError("simple.chance_random_min harus > 0 dan < 99.99.")
        if self.simple_chance_random_max <= 0 or self.simple_chance_random_max >= Decimal("99.99"):
            raise ConfigError("simple.chance_random_max harus > 0 dan < 99.99.")
        if self.simple_chance_random_min > self.simple_chance_random_max:
            raise ConfigError("simple.chance_random_min tidak boleh lebih besar dari chance_random_max.")
        if self.simple_chance_random_precision < 0 or self.simple_chance_random_precision > 8:
            raise ConfigError("simple.chance_random_precision harus 0-8.")
        self.simple_replay_on_take_profit = parse_toggle(
            simple_cfg.get("replay_on_take_profit", "OFF"), "simple.replay_on_take_profit"
        )
        self.simple_replay_on_stop_loss = parse_toggle(
            simple_cfg.get("replay_on_stop_loss", "OFF"), "simple.replay_on_stop_loss"
        )
        self.simple_preset_prompt = parse_toggle(simple_cfg.get("preset_prompt", "ON"), "simple.preset_prompt")
        self.simple_replay_after_sec = float(simple_cfg.get("replay_after_sec", 5))
        self.simple_replay_count = int(simple_cfg.get("replay_count", 0))
        self.simple_replay_done = 0
        if self.simple_replay_after_sec < 0:
            raise ConfigError("simple.replay_after_sec tidak boleh negatif.")
        if self.simple_replay_count < 0:
            raise ConfigError("simple.replay_count tidak boleh negatif.")
        if not self.simple_mode_enabled:
            self.simple_chance_random_enabled = False
            self.simple_hilo_random = False
            self.simple_replay_on_take_profit = False
            self.simple_replay_on_stop_loss = False
            self.simple_preset_prompt = False
            self.simple_replay_after_sec = 0.0
            self.simple_replay_count = 0
            self.simple_fixed_rule = self.rule
        self.base_amount_before_normalize = self.base_amount
        self.base_amount = self._normalize_amount(self.base_amount)
        self.current_amount = self.base_amount
        if self.base_amount <= 0:
            raise ConfigError("bot.base_amount terlalu kecil untuk skala desimal coin saat ini.")

        strategy_cfg = cfg["strategy"]
        self.switch_rule_on_win = parse_toggle(strategy_cfg.get("switch_rule_on_win", "OFF"), "strategy.switch_rule_on_win")
        self.switch_rule_on_loss = parse_toggle(
            strategy_cfg.get("switch_rule_on_loss", "OFF"), "strategy.switch_rule_on_loss"
        )

        on_win_cfg = strategy_cfg.get("on_win", {})
        on_loss_cfg = strategy_cfg.get("on_loss", {})
        self.custom_on_win_reset = parse_toggle(on_win_cfg.get("reset_to_base", "ON"), "strategy.on_win.reset_to_base")
        self.custom_on_loss_reset = parse_toggle(
            on_loss_cfg.get("reset_to_base", "OFF"), "strategy.on_loss.reset_to_base"
        )
        self.custom_on_win_multiplier = to_decimal(on_win_cfg.get("amount_multiplier", 1.0), "strategy.on_win.amount_multiplier")
        self.custom_on_win_addition = to_decimal(on_win_cfg.get("amount_addition", 0.0), "strategy.on_win.amount_addition")
        self.custom_on_loss_multiplier = to_decimal(
            on_loss_cfg.get("amount_multiplier", 2.0), "strategy.on_loss.amount_multiplier"
        )
        self.custom_on_loss_addition = to_decimal(on_loss_cfg.get("amount_addition", 0.0), "strategy.on_loss.amount_addition")

        preset_cfg = strategy_cfg.get("preset", {})
        self.preset_enabled = parse_toggle(preset_cfg.get("enabled", "OFF"), "strategy.preset.enabled")
        self.supported_presets = set(SUPPORTED_PRESETS)
        self.preset_name = resolve_selected_preset(preset_cfg, "strategy.preset")
        if self.preset_name:
            # Jika ada preset.use yang ON, otomatis aktif tanpa harus set preset.enabled=ON.
            self.preset_enabled = True
        if self.preset_enabled and not self.preset_name:
            raise ConfigError("strategy.preset.enabled=ON, tapi belum ada preset yang ON di strategy.preset.use.")

        self.preset_martingale_multiplier = to_decimal(
            preset_cfg.get("martingale_multiplier", 2.0), "strategy.preset.martingale_multiplier"
        )
        self.preset_fibonacci_unit = to_decimal(preset_cfg.get("fibonacci_unit", 1.0), "strategy.preset.fibonacci_unit")
        self.preset_fibonacci_step_back_on_win = int(
            preset_cfg.get("fibonacci_step_back_on_win", 2)
        )
        self.preset_paroli_multiplier = to_decimal(
            preset_cfg.get("paroli_multiplier", 2.0), "strategy.preset.paroli_multiplier"
        )
        self.preset_paroli_max_win_streak = int(preset_cfg.get("paroli_max_win_streak", 3))
        self.preset_dalembert_step = to_decimal(preset_cfg.get("dalembert_step", 1.0), "strategy.preset.dalembert_step")
        self.preset_long_run_loss_multiplier = to_decimal(
            preset_cfg.get("long_run_loss_multiplier", 1.08), "strategy.preset.long_run_loss_multiplier"
        )
        self.preset_long_run_max_steps = int(preset_cfg.get("long_run_max_steps", 8))
        self.preset_long_run_recovery_steps_on_win = int(preset_cfg.get("long_run_recovery_steps_on_win", 2))
        self.preset_long_run_max_scale = to_decimal(preset_cfg.get("long_run_max_scale", 2.0), "strategy.preset.long_run_max_scale")
        self.preset_long_run_shield_after_losses = int(preset_cfg.get("long_run_shield_after_losses", 5))
        self.preset_long_run_shield_rounds = int(preset_cfg.get("long_run_shield_rounds", 2))
        self.preset_mining_v2_loss_multiplier = to_decimal(
            preset_cfg.get("mining_v2_loss_multiplier", 1.03), "strategy.preset.mining_v2_loss_multiplier"
        )
        self.preset_mining_v2_max_steps = int(preset_cfg.get("mining_v2_max_steps", 6))
        self.preset_mining_v2_recovery_steps_on_win = int(
            preset_cfg.get("mining_v2_recovery_steps_on_win", 3)
        )
        self.preset_mining_v2_max_scale = to_decimal(
            preset_cfg.get("mining_v2_max_scale", 1.50), "strategy.preset.mining_v2_max_scale"
        )
        self.preset_mining_v2_cooldown_trigger_losses = int(
            preset_cfg.get("mining_v2_cooldown_trigger_losses", 4)
        )
        self.preset_mining_v2_cooldown_rounds = int(preset_cfg.get("mining_v2_cooldown_rounds", 2))
        self.preset_pro_safe_loss_multiplier = to_decimal(
            preset_cfg.get("pro_safe_loss_multiplier", 1.02), "strategy.preset.pro_safe_loss_multiplier"
        )
        self.preset_pro_safe_max_steps = int(preset_cfg.get("pro_safe_max_steps", 5))
        self.preset_pro_safe_recovery_steps_on_win = int(
            preset_cfg.get("pro_safe_recovery_steps_on_win", 2)
        )
        self.preset_pro_safe_max_scale = to_decimal(
            preset_cfg.get("pro_safe_max_scale", 1.25), "strategy.preset.pro_safe_max_scale"
        )
        self.preset_pro_recovery_loss_multiplier = to_decimal(
            preset_cfg.get("pro_recovery_loss_multiplier", 1.06), "strategy.preset.pro_recovery_loss_multiplier"
        )
        self.preset_pro_recovery_max_steps = int(preset_cfg.get("pro_recovery_max_steps", 6))
        self.preset_pro_recovery_recovery_steps_on_win = int(
            preset_cfg.get("pro_recovery_recovery_steps_on_win", 1)
        )
        self.preset_pro_recovery_max_scale = to_decimal(
            preset_cfg.get("pro_recovery_max_scale", 2.0), "strategy.preset.pro_recovery_max_scale"
        )
        self.preset_pro_recovery_cooldown_trigger_losses = int(
            preset_cfg.get("pro_recovery_cooldown_trigger_losses", 4)
        )
        self.preset_pro_recovery_cooldown_rounds = int(
            preset_cfg.get("pro_recovery_cooldown_rounds", 2)
        )
        self.preset_pro_scalper_win_multiplier = to_decimal(
            preset_cfg.get("pro_scalper_win_multiplier", 1.35), "strategy.preset.pro_scalper_win_multiplier"
        )
        self.preset_pro_scalper_max_win_streak = int(preset_cfg.get("pro_scalper_max_win_streak", 3))
        self.preset_premium_guard_loss_multiplier = to_decimal(
            preset_cfg.get("premium_guard_loss_multiplier", 1.04), "strategy.preset.premium_guard_loss_multiplier"
        )
        self.preset_premium_guard_max_steps = int(preset_cfg.get("premium_guard_max_steps", 5))
        self.preset_premium_guard_max_scale = to_decimal(
            preset_cfg.get("premium_guard_max_scale", 1.40), "strategy.preset.premium_guard_max_scale"
        )
        self.preset_premium_guard_risk_percent = to_decimal(
            preset_cfg.get("premium_guard_risk_percent", 0.03), "strategy.preset.premium_guard_risk_percent"
        )
        self.preset_premium_guard_cooldown_trigger_losses = int(
            preset_cfg.get("premium_guard_cooldown_trigger_losses", 4)
        )
        self.preset_premium_guard_cooldown_rounds = int(
            preset_cfg.get("premium_guard_cooldown_rounds", 2)
        )
        self.preset_premium_compound_loss_multiplier = to_decimal(
            preset_cfg.get("premium_compound_loss_multiplier", 1.03),
            "strategy.preset.premium_compound_loss_multiplier",
        )
        self.preset_premium_compound_max_steps = int(preset_cfg.get("premium_compound_max_steps", 5))
        self.preset_premium_compound_recovery_steps_on_win = int(
            preset_cfg.get("premium_compound_recovery_steps_on_win", 2)
        )
        self.preset_premium_compound_max_scale = to_decimal(
            preset_cfg.get("premium_compound_max_scale", 1.60), "strategy.preset.premium_compound_max_scale"
        )
        self.preset_premium_compound_profit_boost_percent = to_decimal(
            preset_cfg.get("premium_compound_profit_boost_percent", 15.0),
            "strategy.preset.premium_compound_profit_boost_percent",
        )
        self.preset_premium_daily_target_percent = to_decimal(
            preset_cfg.get("premium_daily_target_percent", 10), "strategy.preset.premium_daily_target_percent"
        )
        self.preset_premium_stop_loss_percent = to_decimal(
            preset_cfg.get("premium_stop_loss_percent", 5), "strategy.preset.premium_stop_loss_percent"
        )
        self.preset_premium_risk_percent = to_decimal(
            preset_cfg.get("premium_risk_percent", 0.05), "strategy.preset.premium_risk_percent"
        )
        self.preset_premium_max_risk_percent = to_decimal(
            preset_cfg.get("premium_max_risk_percent", 0.25), "strategy.preset.premium_max_risk_percent"
        )
        self.preset_premium_loss_multiplier = to_decimal(
            preset_cfg.get("premium_loss_multiplier", 1.06), "strategy.preset.premium_loss_multiplier"
        )
        self.preset_premium_max_steps = int(preset_cfg.get("premium_max_steps", 5))
        self.preset_premium_recovery_steps_on_win = int(
            preset_cfg.get("premium_recovery_steps_on_win", 2)
        )
        self.preset_premium_max_scale = to_decimal(
            preset_cfg.get("premium_max_scale", 1.35), "strategy.preset.premium_max_scale"
        )
        self.preset_premium_cooldown_trigger_losses = int(
            preset_cfg.get("premium_cooldown_trigger_losses", 4)
        )
        self.preset_premium_cooldown_rounds = int(preset_cfg.get("premium_cooldown_rounds", 2))

        if self.preset_martingale_multiplier <= Decimal("0"):
            raise ConfigError("strategy.preset.martingale_multiplier harus > 0.")
        if self.preset_fibonacci_unit <= Decimal("0"):
            raise ConfigError("strategy.preset.fibonacci_unit harus > 0.")
        if self.preset_fibonacci_step_back_on_win < 0:
            raise ConfigError("strategy.preset.fibonacci_step_back_on_win tidak boleh negatif.")
        if self.preset_paroli_multiplier <= Decimal("0"):
            raise ConfigError("strategy.preset.paroli_multiplier harus > 0.")
        if self.preset_paroli_max_win_streak < 1:
            raise ConfigError("strategy.preset.paroli_max_win_streak minimal 1.")
        if self.preset_dalembert_step <= Decimal("0"):
            raise ConfigError("strategy.preset.dalembert_step harus > 0.")
        if self.preset_long_run_loss_multiplier < Decimal("1"):
            raise ConfigError("strategy.preset.long_run_loss_multiplier harus >= 1.")
        if self.preset_long_run_max_steps < 0:
            raise ConfigError("strategy.preset.long_run_max_steps tidak boleh negatif.")
        if self.preset_long_run_recovery_steps_on_win < 0:
            raise ConfigError("strategy.preset.long_run_recovery_steps_on_win tidak boleh negatif.")
        if self.preset_long_run_max_scale < Decimal("1"):
            raise ConfigError("strategy.preset.long_run_max_scale minimal 1.")
        if self.preset_long_run_shield_after_losses < 0:
            raise ConfigError("strategy.preset.long_run_shield_after_losses tidak boleh negatif.")
        if self.preset_long_run_shield_rounds < 0:
            raise ConfigError("strategy.preset.long_run_shield_rounds tidak boleh negatif.")
        if self.preset_mining_v2_loss_multiplier < Decimal("1"):
            raise ConfigError("strategy.preset.mining_v2_loss_multiplier harus >= 1.")
        if self.preset_mining_v2_max_steps < 0:
            raise ConfigError("strategy.preset.mining_v2_max_steps tidak boleh negatif.")
        if self.preset_mining_v2_recovery_steps_on_win < 0:
            raise ConfigError("strategy.preset.mining_v2_recovery_steps_on_win tidak boleh negatif.")
        if self.preset_mining_v2_max_scale < Decimal("1"):
            raise ConfigError("strategy.preset.mining_v2_max_scale minimal 1.")
        if self.preset_mining_v2_cooldown_trigger_losses < 0:
            raise ConfigError("strategy.preset.mining_v2_cooldown_trigger_losses tidak boleh negatif.")
        if self.preset_mining_v2_cooldown_rounds < 0:
            raise ConfigError("strategy.preset.mining_v2_cooldown_rounds tidak boleh negatif.")
        if self.preset_pro_safe_loss_multiplier < Decimal("1"):
            raise ConfigError("strategy.preset.pro_safe_loss_multiplier harus >= 1.")
        if self.preset_pro_safe_max_steps < 0:
            raise ConfigError("strategy.preset.pro_safe_max_steps tidak boleh negatif.")
        if self.preset_pro_safe_recovery_steps_on_win < 0:
            raise ConfigError("strategy.preset.pro_safe_recovery_steps_on_win tidak boleh negatif.")
        if self.preset_pro_safe_max_scale < Decimal("1"):
            raise ConfigError("strategy.preset.pro_safe_max_scale minimal 1.")
        if self.preset_pro_recovery_loss_multiplier < Decimal("1"):
            raise ConfigError("strategy.preset.pro_recovery_loss_multiplier harus >= 1.")
        if self.preset_pro_recovery_max_steps < 0:
            raise ConfigError("strategy.preset.pro_recovery_max_steps tidak boleh negatif.")
        if self.preset_pro_recovery_recovery_steps_on_win < 0:
            raise ConfigError("strategy.preset.pro_recovery_recovery_steps_on_win tidak boleh negatif.")
        if self.preset_pro_recovery_max_scale < Decimal("1"):
            raise ConfigError("strategy.preset.pro_recovery_max_scale minimal 1.")
        if self.preset_pro_recovery_cooldown_trigger_losses < 0:
            raise ConfigError("strategy.preset.pro_recovery_cooldown_trigger_losses tidak boleh negatif.")
        if self.preset_pro_recovery_cooldown_rounds < 0:
            raise ConfigError("strategy.preset.pro_recovery_cooldown_rounds tidak boleh negatif.")
        if self.preset_pro_scalper_win_multiplier <= Decimal("1"):
            raise ConfigError("strategy.preset.pro_scalper_win_multiplier harus > 1.")
        if self.preset_pro_scalper_max_win_streak < 1:
            raise ConfigError("strategy.preset.pro_scalper_max_win_streak minimal 1.")
        if self.preset_premium_guard_loss_multiplier < Decimal("1"):
            raise ConfigError("strategy.preset.premium_guard_loss_multiplier harus >= 1.")
        if self.preset_premium_guard_max_steps < 0:
            raise ConfigError("strategy.preset.premium_guard_max_steps tidak boleh negatif.")
        if self.preset_premium_guard_max_scale < Decimal("1"):
            raise ConfigError("strategy.preset.premium_guard_max_scale minimal 1.")
        if self.preset_premium_guard_risk_percent <= Decimal("0"):
            raise ConfigError("strategy.preset.premium_guard_risk_percent harus > 0.")
        if self.preset_premium_guard_cooldown_trigger_losses < 0:
            raise ConfigError("strategy.preset.premium_guard_cooldown_trigger_losses tidak boleh negatif.")
        if self.preset_premium_guard_cooldown_rounds < 0:
            raise ConfigError("strategy.preset.premium_guard_cooldown_rounds tidak boleh negatif.")
        if self.preset_premium_compound_loss_multiplier < Decimal("1"):
            raise ConfigError("strategy.preset.premium_compound_loss_multiplier harus >= 1.")
        if self.preset_premium_compound_max_steps < 0:
            raise ConfigError("strategy.preset.premium_compound_max_steps tidak boleh negatif.")
        if self.preset_premium_compound_recovery_steps_on_win < 0:
            raise ConfigError("strategy.preset.premium_compound_recovery_steps_on_win tidak boleh negatif.")
        if self.preset_premium_compound_max_scale < Decimal("1"):
            raise ConfigError("strategy.preset.premium_compound_max_scale minimal 1.")
        if self.preset_premium_compound_profit_boost_percent < Decimal("0"):
            raise ConfigError("strategy.preset.premium_compound_profit_boost_percent tidak boleh negatif.")
        if self.preset_premium_daily_target_percent < Decimal("0"):
            raise ConfigError("strategy.preset.premium_daily_target_percent tidak boleh negatif.")
        if self.preset_premium_stop_loss_percent < Decimal("0"):
            raise ConfigError("strategy.preset.premium_stop_loss_percent tidak boleh negatif.")
        if self.preset_premium_risk_percent <= Decimal("0"):
            raise ConfigError("strategy.preset.premium_risk_percent harus > 0.")
        if self.preset_premium_max_risk_percent <= Decimal("0"):
            raise ConfigError("strategy.preset.premium_max_risk_percent harus > 0.")
        if self.preset_premium_max_risk_percent < self.preset_premium_risk_percent:
            raise ConfigError("strategy.preset.premium_max_risk_percent harus >= premium_risk_percent.")
        if self.preset_premium_loss_multiplier < Decimal("1"):
            raise ConfigError("strategy.preset.premium_loss_multiplier harus >= 1.")
        if self.preset_premium_max_steps < 0:
            raise ConfigError("strategy.preset.premium_max_steps tidak boleh negatif.")
        if self.preset_premium_recovery_steps_on_win < 0:
            raise ConfigError("strategy.preset.premium_recovery_steps_on_win tidak boleh negatif.")
        if self.preset_premium_max_scale < Decimal("1"):
            raise ConfigError("strategy.preset.premium_max_scale minimal 1.")
        if self.preset_premium_cooldown_trigger_losses < 0:
            raise ConfigError("strategy.preset.premium_cooldown_trigger_losses tidak boleh negatif.")
        if self.preset_premium_cooldown_rounds < 0:
            raise ConfigError("strategy.preset.premium_cooldown_rounds tidak boleh negatif.")

        self.fibonacci_index = 0
        self.paroli_step = 0
        self.dalembert_level = 0
        self.long_run_step = 0
        self.long_run_shield_remaining = 0
        self.mining_v2_step = 0
        self.mining_v2_cooldown_remaining = 0
        self.pro_safe_step = 0
        self.pro_recovery_step = 0
        self.pro_recovery_cooldown_remaining = 0
        self.pro_scalper_streak = 0
        self.premium_guard_step = 0
        self.premium_guard_cooldown_remaining = 0
        self.premium_compound_step = 0
        self.premium_step = 0
        self.premium_cooldown_remaining = 0
        self.fibonacci_cache = [1, 1]

        self.total_profit = Decimal("0")
        self.current_balance = Decimal("0")
        self.api_balance = Decimal("0")
        self.estimated_balance = Decimal("0")
        self.balance_source = "API"
        self.start_balance = Decimal("0")
        self.premium_target_profit_abs = Decimal("0")
        self.premium_stop_loss_abs = Decimal("0")
        self.bet_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.api_error_count = 0
        self.started_at = time.time()
        self.sticky_footer_lines = 4
        self.client.set_runtime_warn_logger(self.warn)
        self.last_bet_time = "--:--:--"
        self.last_bet_roll = "-"
        self.last_bet_state = "WAIT"
        self.last_bet_multiplier = self.multiplier
        self.last_bet_amount = self.current_amount
        self.last_bet_profit = Decimal("0")
        self.last_bet_balance = self.current_balance
        self.last_bet_total_profit = self.total_profit
        self.active_sync_mode = self._detect_auto_sync_mode()

        self.sync_bet_pair()

    def now_prefix(self) -> str:
        if not self.show_timestamp:
            return ""
        return datetime.now().strftime("[%H:%M:%S] ")

    def _prepare_sticky_layout(self) -> Tuple[int, int, int] | None:
        if not self.sticky_footer_enabled:
            return None

        size = shutil.get_terminal_size(fallback=(120, 30))
        content_bottom = size.lines - self.sticky_footer_lines
        if content_bottom < 1:
            self.sticky_footer_enabled = False
            return None

        current_size = (size.columns, size.lines)
        if not self._sticky_region_active or self._sticky_region_size != current_size:
            sys.stdout.write(f"\x1b[1;{content_bottom}r")
            self._sticky_region_active = True
            self._sticky_region_size = current_size
            sys.stdout.flush()

        return size.columns, size.lines, content_bottom

    def _reset_sticky_layout(self) -> None:
        if not self._sticky_region_active:
            return
        sys.stdout.write("\x1b[r")
        sys.stdout.flush()
        self._sticky_region_active = False
        self._sticky_region_size = (0, 0)

    def _emit_runtime_lines(self, lines: Iterable[str]) -> None:
        rendered = list(lines)
        if not rendered:
            return
        if self.sticky_footer_enabled:
            self._clear_sticky_footer()
        for line in rendered:
            print(line)
        if self.sticky_footer_enabled:
            self._render_sticky_footer()

    def _emit_runtime_line(self, line: str) -> None:
        self._emit_runtime_lines((line,))

    def info(self, message: str) -> None:
        plain = self._fit_width(self.now_prefix() + message)
        self._emit_runtime_line(THEME_PRIMARY + plain)

    def success(self, message: str) -> None:
        plain = self._fit_width(self.now_prefix() + message)
        self._emit_runtime_line(THEME_TEXT_BRIGHT + plain)

    def warn(self, message: str) -> None:
        plain = self._fit_width(self.now_prefix() + message)
        self._emit_runtime_line(THEME_SECONDARY + plain)

    def error(self, message: str) -> None:
        plain = self._fit_width(self.now_prefix() + message)
        self._emit_runtime_line(THEME_SECONDARY_BRIGHT + plain)

    def _terminal_width(self) -> int:
        if self.history_width > 0:
            return self.history_width
        try:
            return shutil.get_terminal_size(fallback=(120, 20)).columns
        except OSError:
            return 120

    def _fit_width(self, text: str) -> str:
        width = self._terminal_width()
        if width <= 0 or len(text) <= width:
            return text
        if width <= 1:
            return text[:width]
        return text[: width - 1] + "~"

    def _fit_exact_width(self, text: str, width: int) -> str:
        if width <= 0:
            return text
        if len(text) >= width:
            return text[:width]
        return text + (" " * (width - len(text)))

    def _safe_decimal(self, value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError):
            raise APIError(f"Nilai numerik tidak valid dari API: {value}")

    def _format_roll(self, value: Any) -> str:
        try:
            return format_decimal(Decimal(str(value)), 2)
        except (InvalidOperation, TypeError):
            return str(value)

    def _signed_decimal(self, value: Decimal, places: int) -> str:
        sign = "+" if value >= 0 else "-"
        amount = value.copy_abs()
        if places <= 0:
            rounded = amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            if rounded == 0 and amount > 0:
                rounded = Decimal("1")
            return f"{sign}{format_decimal(rounded, 0)}"

        step = Decimal("1").scaleb(-places)
        rounded = amount.quantize(step, rounding=ROUND_HALF_UP)
        if rounded == 0 and amount > 0:
            rounded = step
        return f"{sign}{format_decimal(rounded, places)}"

    def _format_rupiah(self, value: Decimal, signed: bool = False) -> str:
        amount = value
        sign = ""
        if signed:
            sign = "+" if amount >= 0 else "-"
            amount = amount.copy_abs()

        rounded = amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        grouped = f"{int(rounded):,}".replace(",", ".")
        prefix = f"{sign}Rp" if signed else "Rp"
        return f"{prefix}{grouped}"

    def _format_rupiah_micro(self, value: Decimal, signed: bool = False, places: int = 4) -> str:
        amount = value
        sign = ""
        if signed:
            sign = "+" if amount >= 0 else "-"
            amount = amount.copy_abs()

        quant = Decimal("1").scaleb(-places)
        rounded = amount.quantize(quant, rounding=ROUND_HALF_UP)
        if rounded == 0 and amount > 0:
            rounded = quant
        raw = format(rounded, f".{places}f")
        int_part, frac_part = raw.split(".")
        grouped = f"{int(int_part):,}".replace(",", ".")
        prefix = f"{sign}Rp" if signed else "Rp"
        return f"{prefix}{grouped}.{frac_part}"

    def _refresh_idr_price(self, force: bool = False) -> None:
        if not self.show_idr_value:
            return
        if not self.idr_coin_id:
            return

        now_ts = time.time()
        if not force and self.idr_refresh_seconds > 0:
            if now_ts - self.idr_last_update_ts < self.idr_refresh_seconds:
                return

        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": self.idr_coin_id, "vs_currencies": "idr"},
                headers={"Accept": "application/json", "User-Agent": "NUSANTARA-BOT/1.0"},
                timeout=8,
            )
            if not response.ok:
                raise APIError(f"HTTP {response.status_code}")

            payload = response.json()
            idr_value = payload.get(self.idr_coin_id, {}).get("idr")
            if idr_value is None:
                raise APIError("field 'idr' tidak ditemukan di response price")

            idr_price = Decimal(str(idr_value))
            if idr_price <= 0:
                raise APIError("harga IDR tidak valid (<= 0)")

            self.idr_price = idr_price
            self.idr_last_update_ts = now_ts
            self.idr_last_update_at = datetime.now().strftime("%H:%M:%S")
            self.idr_status = "OK"
            self.idr_error_notified = False
        except Exception as exc:
            self.idr_status = "ERROR"
            if not self.idr_error_notified:
                self.warn(f"Gagal update harga IDR: {exc}")
                self.idr_error_notified = True

    def _normalize_amount(self, amount: Decimal) -> Decimal:
        normalized = quantize_places(amount, self.coin_decimal_places)
        if amount > 0 and normalized <= 0:
            return Decimal("1").scaleb(-self.coin_decimal_places)
        return normalized

    def _clear_sticky_footer(self) -> None:
        layout = self._prepare_sticky_layout()
        if layout is None:
            return
        _, lines, _ = layout
        start_line = max(1, lines - self.sticky_footer_lines + 1)
        sys.stdout.write("\x1b[s")
        for idx in range(self.sticky_footer_lines):
            sys.stdout.write(f"\x1b[{start_line + idx};1H")
            sys.stdout.write("\x1b[2K")
        sys.stdout.write("\x1b[u")
        sys.stdout.flush()

    def _update_last_bet_snapshot(
        self,
        state: str,
        amount: Decimal,
        result_value: Any,
        profit: Decimal,
    ) -> None:
        if state == "win":
            status = "WIN"
        elif state == "loss":
            status = "LOSS"
        else:
            status = "WAIT"

        self.last_bet_time = datetime.now().strftime("%H:%M:%S") if self.show_timestamp else "--:--:--"
        self.last_bet_roll = self._format_roll(result_value)
        self.last_bet_state = status
        self.last_bet_multiplier = self.multiplier
        self.last_bet_amount = amount
        self.last_bet_profit = profit
        self.last_bet_balance = self.current_balance
        self.last_bet_total_profit = self.total_profit

    def _render_sticky_footer(self) -> None:
        layout = self._prepare_sticky_layout()
        if layout is None:
            return

        columns, lines, _ = layout
        start_line = max(1, lines - self.sticky_footer_lines + 1)
        winrate = Decimal("0")
        if self.bet_count > 0:
            winrate = (Decimal(self.win_count) / Decimal(self.bet_count)) * Decimal("100")

        row_profit_col = self._signed_decimal(self.last_bet_profit, self.profit_display_precision)
        row_total_col = self._signed_decimal(self.last_bet_total_profit, self.profit_display_precision)
        stats_total_col = self._signed_decimal(self.total_profit, self.profit_display_precision)
        last_multiplier = format_decimal(self.last_bet_multiplier, self.multiplier_precision)
        last_amount = format_decimal(self.last_bet_amount, self.amount_display_precision)
        last_balance = format_decimal(self.last_bet_balance, self.balance_display_precision)
        last_roll = self.last_bet_roll
        wr_col = format_decimal(winrate, 2)
        bal_col = format_decimal(self.current_balance, self.balance_display_precision)
        idr_enabled = self.show_idr_value and self.idr_price > 0
        bal_idr_col = self._format_rupiah(self.current_balance * self.idr_price) if idr_enabled else "n/a"
        total_idr_col = self._format_rupiah(self.total_profit * self.idr_price, signed=True) if idr_enabled else "n/a"

        def choose_line(options: Tuple[str, ...]) -> str:
            for text in options:
                if len(text) <= columns:
                    return text
            return options[-1]

        if columns >= 136:
            header = (
                f"{'TIME':<8} | {'ROLL':>7} | {'WIN/LOSS':<8} | {'MULTI':>12} | "
                f"{'AMOUNT':>14} | {'PROFIT':>14} | {('BALANCE ' + self.currency_display):>14} | {'TOTAL PROFIT':>14}"
            )
            row = (
                f"{self.last_bet_time:<8} | {last_roll:>7} | {self.last_bet_state:<8} | "
                f"{last_multiplier:>12} | {last_amount:>14} | {row_profit_col:>14} | "
                f"{last_balance:>14} | {row_total_col:>14}"
            )
            stats = (
                f"STATS | BET:{self.bet_count:<6} WIN:{self.win_count:<6} LOSS:{self.loss_count:<6} "
                f"WR:{wr_col:>6}% | BALANCE {self.currency_display}:{bal_col:>14}"
            )
            if idr_enabled:
                total_line = choose_line(
                    (
                        f"BALANCE IDR: {bal_idr_col} | TOTAL PROFIT {self.currency_display}: {stats_total_col} | "
                        f"TOTAL PROFIT IDR: {total_idr_col}",
                        f"BALANCE IDR: {bal_idr_col} | TOTAL PROFIT {self.currency_display}: {stats_total_col}",
                        f"BALANCE IDR: {bal_idr_col} | TOTAL PROFIT IDR: {total_idr_col}",
                        f"BALANCE IDR: {bal_idr_col}",
                        f"TOTAL PROFIT {self.currency_display}: {stats_total_col}",
                    )
                )
            else:
                total_line = f"TOTAL PROFIT {self.currency_display}: {stats_total_col}"
        elif columns >= 108:
            header = (
                f"{'TIME':<8} | {'ROLL':>7} | {'RESULT':<6} | {'MULTI':>8} | {'AMOUNT':>10} | "
                f"{'PROFIT':>11} | {'BALANCE':>11} | {'TOTAL':>11}"
            )
            row = (
                f"{self.last_bet_time:<8} | {last_roll:>7} | {self.last_bet_state:<6} | {last_multiplier:>8} | "
                f"{last_amount:>10} | {row_profit_col:>11} | {last_balance:>11} | {row_total_col:>11}"
            )
            stats = (
                f"STATS BET:{self.bet_count} WIN:{self.win_count} LOSS:{self.loss_count} WR:{wr_col}% "
                f"BALANCE:{bal_col}"
            )
            if idr_enabled:
                total_line = choose_line(
                    (
                        f"BALANCE IDR: {bal_idr_col} | TOTAL PROFIT {self.currency_display}: {stats_total_col} | "
                        f"TOTAL PROFIT IDR: {total_idr_col}",
                        f"BALANCE IDR: {bal_idr_col} | TOTAL PROFIT {self.currency_display}: {stats_total_col}",
                        f"BALANCE IDR: {bal_idr_col} | TOTAL PROFIT IDR: {total_idr_col}",
                        f"BALANCE IDR: {bal_idr_col}",
                        f"TOTAL PROFIT {self.currency_display}: {stats_total_col}",
                    )
                )
            else:
                total_line = f"TOTAL PROFIT {self.currency_display}: {stats_total_col}"
        elif columns >= 82:
            header = (
                f"{'TIME':<8} | {'ROLL':>7} | {'RESULT':<6} | {'PROFIT':>12} | {'TOTAL':>12}"
            )
            row = (
                f"{self.last_bet_time:<8} | {last_roll:>7} | {self.last_bet_state:<6} | "
                f"{row_profit_col:>12} | {row_total_col:>12}"
            )
            stats = (
                f"BET:{self.bet_count} WIN:{self.win_count} LOSS:{self.loss_count} WR:{wr_col}% "
                f"BALANCE:{bal_col}"
            )
            if idr_enabled:
                total_line = choose_line(
                    (
                        f"BALANCE IDR: {bal_idr_col} | TOTAL {self.currency_display}: {stats_total_col} | TOTAL IDR: {total_idr_col}",
                        f"BALANCE IDR: {bal_idr_col} | TOTAL {self.currency_display}: {stats_total_col}",
                        f"BALANCE IDR: {bal_idr_col} | TOTAL IDR: {total_idr_col}",
                        f"BALANCE IDR: {bal_idr_col}",
                        f"TOTAL {self.currency_display}: {stats_total_col}",
                    )
                )
            else:
                total_line = f"TOTAL {self.currency_display}: {stats_total_col}"
        else:
            header = "TIME | RESULT | PROFIT | TOTAL"
            row = (
                f"{self.last_bet_time} | {self.last_bet_state} | {row_profit_col} | {row_total_col}"
            )
            stats = (
                f"BET:{self.bet_count} WR:{wr_col}% BAL:{bal_col}"
            )
            if idr_enabled:
                total_line = choose_line(
                    (
                        f"BALANCE IDR: {bal_idr_col} | {self.currency_display} {stats_total_col}",
                        f"BALANCE IDR: {bal_idr_col}",
                        f"{self.currency_display} {stats_total_col}",
                    )
                )
            else:
                total_line = f"{self.currency_display} {stats_total_col}"

        header = self._fit_exact_width(header, columns)
        row = self._fit_exact_width(row, columns)
        stats = self._fit_exact_width(stats, columns)
        total_line = self._fit_exact_width(total_line, columns)

        header_color = THEME_TEXT_DIM
        if self.last_bet_state == "WIN":
            row_color = THEME_PRIMARY_BRIGHT
        elif self.last_bet_state == "LOSS":
            row_color = THEME_SECONDARY_BRIGHT
        else:
            row_color = THEME_TEXT
        stats_color = THEME_TEXT_BRIGHT
        if self.total_profit > 0:
            total_color = THEME_PRIMARY_BRIGHT
        elif self.total_profit < 0:
            total_color = THEME_SECONDARY_BRIGHT
        else:
            total_color = THEME_TEXT_BRIGHT

        sys.stdout.write("\x1b[s")
        sys.stdout.write(f"\x1b[{start_line};1H")
        sys.stdout.write("\x1b[2K")
        sys.stdout.write(header_color + header + Style.RESET_ALL)
        sys.stdout.write(f"\x1b[{start_line + 1};1H")
        sys.stdout.write("\x1b[2K")
        sys.stdout.write(row_color + row + Style.RESET_ALL)
        sys.stdout.write(f"\x1b[{start_line + 2};1H")
        sys.stdout.write("\x1b[2K")
        sys.stdout.write(stats_color + stats + Style.RESET_ALL)
        sys.stdout.write(f"\x1b[{start_line + 3};1H")
        sys.stdout.write("\x1b[2K")
        sys.stdout.write(total_color + total_line + Style.RESET_ALL)
        sys.stdout.write("\x1b[u")
        sys.stdout.flush()

    def _print_history_header(self) -> None:
        header = (
            f"{'TIME':<8} | {'ROLL':>7} | {'WIN/LOSS':<8} | {'MULTI':>12} | "
            f"{'AMOUNT':>14} | {'PROFIT':>14} | {('BALANCE ' + self.currency_display):>14} | {'TOTAL PROFIT':>14}"
        )
        line = "-" * len(header)
        self._emit_runtime_lines(
            (
                THEME_TEXT + self._fit_width(header),
                THEME_TEXT_DIM + self._fit_width(line),
            )
        )

    def _history_line(
        self,
        state: str,
        amount: Decimal,
        result_value: Any,
        profit: Decimal,
    ) -> str:
        time_col = datetime.now().strftime("%H:%M:%S") if self.show_timestamp else "--:--:--"
        status = "WIN" if state == "win" else "LOSS"
        amount_col = format_decimal(amount, self.amount_display_precision)
        mult_col = format_decimal(self.multiplier, self.multiplier_precision)
        roll_col = self._format_roll(result_value)
        profit_col = self._signed_decimal(profit, self.profit_display_precision)
        total_col = self._signed_decimal(self.total_profit, self.profit_display_precision)
        balance_col = format_decimal(self.current_balance, self.balance_display_precision)

        line = (
            f"{time_col:<8} | {roll_col:>7} | {status:<8} | {mult_col:>12} | "
            f"{amount_col:>14} | {profit_col:>14} | {balance_col:>14} | {total_col:>14}"
        )
        return self._fit_width(line)

    def _print_mining_log(self, state: str, amount: Decimal, result_value: Any, profit: Decimal) -> None:
        time_col = datetime.now().strftime("%H:%M:%S") if self.show_timestamp else "--:--:--"
        roll_col = self._format_roll(result_value)
        state_text = "WIN" if state == "win" else "LOSS"
        state_color = THEME_PRIMARY_BRIGHT if state == "win" else THEME_SECONDARY_BRIGHT
        profit_col = self._signed_decimal(profit, self.profit_display_precision)
        total_col = self._signed_decimal(self.total_profit, self.profit_display_precision)
        amount_col = format_decimal(amount, self.amount_display_precision)
        mult_col = format_decimal(self.multiplier, self.multiplier_precision)
        profit_idr_col = ""
        if self.show_idr_value and self.idr_price > 0:
            profit_idr_col = self._format_rupiah_micro(profit * self.idr_price, signed=True, places=4)
        width = self._terminal_width()

        if width >= 150:
            if profit_idr_col:
                line_plain = (
                    f"[{time_col}] #{self.bet_count:<5} {state_text:<4} | ROLL {roll_col:>6} | "
                    f"MULTI {mult_col:>8} | AMOUNT {amount_col:>12} {self.currency_display} | "
                    f"PROFIT {profit_col:>12} {self.currency_display} | PROFIT IDR {profit_idr_col:>14} | "
                    f"TOTAL {total_col:>12} {self.currency_display}"
                )
            else:
                line_plain = (
                    f"[{time_col}] #{self.bet_count:<5} {state_text:<4} | ROLL {roll_col:>6} | "
                    f"MULTI {mult_col:>8} | AMOUNT {amount_col:>12} {self.currency_display} | "
                    f"PROFIT {profit_col:>12} {self.currency_display} | TOTAL {total_col:>12} {self.currency_display}"
                )
        elif width >= 125:
            line_plain = (
                f"[{time_col}] #{self.bet_count} {state_text} | ROLL {roll_col} | MULTI {mult_col} | "
                f"AMOUNT {amount_col} | PROFIT {profit_col} | TOTAL {total_col}"
            )
            if profit_idr_col and len(line_plain + f" | PROFIT IDR {profit_idr_col}") <= width:
                line_plain += f" | PROFIT IDR {profit_idr_col}"
        elif width >= 100:
            line_plain = (
                f"[{time_col}] #{self.bet_count} {state_text} | ROLL {roll_col} | "
                f"PROFIT {profit_col} | TOTAL {total_col}"
            )
            if profit_idr_col and len(line_plain + f" | PROFIT IDR {profit_idr_col}") <= width:
                line_plain += f" | PROFIT IDR {profit_idr_col}"
        elif width >= 80:
            line_plain = (
                f"[{time_col}] {state_text} | ROLL {roll_col} | PROFIT {profit_col} | TOTAL {total_col}"
            )
        else:
            line_plain = (
                f"[{time_col}] {state_text} | PROFIT {profit_col} | TOTAL {total_col}"
            )

        line_plain = self._fit_width(line_plain)
        self._emit_runtime_line(state_color + line_plain + Style.RESET_ALL)

    def _update_balances(self, user_balance: Dict[str, Any], profit: Decimal) -> None:
        self.estimated_balance += profit
        api_updated = False

        if isinstance(user_balance, dict) and user_balance.get("amount") is not None:
            try:
                api_balance = self._safe_decimal(user_balance.get("amount"))
                if api_balance != self.api_balance:
                    api_updated = True
                self.api_balance = api_balance
            except APIError as exc:
                self.warn(f"Format user_balance tidak valid: {exc}")

        if self.balance_sync_mode == "api":
            self.current_balance = self.api_balance
            self.balance_source = "API"
        elif self.balance_sync_mode == "estimated":
            self.current_balance = self.estimated_balance
            self.balance_source = "EST"
        else:
            if api_updated:
                self.current_balance = self.api_balance
                self.estimated_balance = self.api_balance
                self.balance_source = "API"
            else:
                self.current_balance = self.estimated_balance
                self.balance_source = "EST"

    def _refresh_balance_periodically(self) -> None:
        if self.balance_refresh_every <= 0:
            return
        if self.bet_count <= 0 or self.bet_count % self.balance_refresh_every != 0:
            return

        try:
            live_balance = self.get_currency_balance()
        except APIError as exc:
            self.warn(f"Gagal refresh balance periodik: {exc}")
            return

        self.api_balance = live_balance
        self.estimated_balance = live_balance
        self.current_balance = live_balance
        self.balance_source = "API"

    def chance_from_bet_value(self, bet_value: Decimal, rule: str) -> Decimal:
        if rule == "under":
            return bet_value
        return Decimal("99.99") - bet_value

    def compute_multiplier(self, bet_value: Decimal, rule: str) -> Decimal:
        chance = self.chance_from_bet_value(bet_value, rule)
        if chance <= Decimal("0"):
            raise ConfigError("Chance hasil kalkulasi <= 0. Ubah bot.bet_value / bot.rule.")
        raw_multiplier = Decimal("99") / chance
        return quantize_places_half_up(raw_multiplier, self.multiplier_precision)

    def compute_bet_value_from_multiplier(self, multiplier: Decimal, rule: str) -> Decimal:
        if multiplier <= Decimal("1"):
            raise ConfigError("Multiplier harus > 1 untuk hitung bet_value.")

        chance = Decimal("99") / multiplier
        chance = quantize_places_half_up(chance, self.bet_value_precision)
        if rule == "under":
            bet_value = chance
        else:
            bet_value = Decimal("99.99") - chance

        bet_value = quantize_places_half_up(bet_value, self.bet_value_precision)
        if bet_value <= Decimal("0") or bet_value >= Decimal("99.99"):
            raise ConfigError("Hasil bet_value dari multiplier di luar batas valid (0 - 99.99).")
        return bet_value

    def _is_pair_value_changed(self, current: Decimal, previous: Decimal, places: int) -> bool:
        current_q = quantize_places(current, places)
        previous_q = quantize_places(previous, places)
        return current_q != previous_q

    def _detect_auto_sync_mode(self) -> str:
        if self.sync_mode != "auto":
            return self.sync_mode
        if self.auto_multiplier:
            return "lock_bet_value"

        has_last_sync = self.last_synced_multiplier > 0 and self.last_synced_bet_value > 0
        if not has_last_sync:
            return self.sync_fallback_mode

        changed_multiplier = self._is_pair_value_changed(
            self.input_multiplier, self.last_synced_multiplier, self.multiplier_precision
        )
        changed_bet_value = self._is_pair_value_changed(
            self.input_bet_value, self.last_synced_bet_value, self.bet_value_precision
        )

        if changed_multiplier and not changed_bet_value:
            return "lock_multiplier"
        if changed_bet_value and not changed_multiplier:
            return "lock_bet_value"
        return self.sync_fallback_mode

    def _effective_sync_mode(self) -> str:
        if self.auto_multiplier:
            return "lock_bet_value"
        if self.sync_mode == "auto":
            return self.active_sync_mode
        return self.sync_mode

    def sync_bet_pair(self) -> None:
        self.bet_value = quantize_places_half_up(self.bet_value, self.bet_value_precision)
        if self.bet_value <= Decimal("0") or self.bet_value >= Decimal("99.99"):
            raise ConfigError("bot.bet_value harus > 0 dan < 99.99.")

        self.multiplier = quantize_places_half_up(self.multiplier, self.multiplier_precision)
        active_mode = self._effective_sync_mode()
        if active_mode == "lock_bet_value":
            self.multiplier = self.compute_multiplier(self.bet_value, self.rule)
            # Sync balik bet_value dari multiplier agar akurat 100% di mata API
            self.bet_value = self.compute_bet_value_from_multiplier(self.multiplier, self.rule)
            return

        if active_mode == "lock_multiplier":
            self.bet_value = self.compute_bet_value_from_multiplier(self.multiplier, self.rule)
            # Paksa update multiplier agar sesuai dengan bet_value yang baru dihitung (grid chance)
            self.multiplier = self.compute_multiplier(self.bet_value, self.rule)

    def _simple_random_chance(self) -> Decimal:
        raw = Decimal(str(random.uniform(float(self.simple_chance_random_min), float(self.simple_chance_random_max))))
        chance = quantize_places_half_up(raw, self.simple_chance_random_precision)
        if chance <= Decimal("0"):
            chance = Decimal("0.01")
        if chance >= Decimal("99.99"):
            chance = Decimal("99.98")
        return chance

    def _apply_simple_runtime_controls_before_bet(self) -> None:
        if not self.simple_mode_enabled:
            return

        if self.simple_hilo_random:
            self.rule = random.choice(["under", "over"])
        else:
            self.rule = self.simple_fixed_rule

        if self.simple_chance_random_enabled:
            self.sync_mode = "lock_bet_value"
            self.active_sync_mode = "lock_bet_value"
            random_chance = self._simple_random_chance()
            if self.rule == "under":
                self.bet_value = random_chance
            else:
                self.bet_value = Decimal("99.99") - random_chance
            self.bet_value = quantize_places_half_up(self.bet_value, self.bet_value_precision)
            self.multiplier = self.compute_multiplier(self.bet_value, self.rule)
            # Sync balik bet_value dari multiplier agar akurat 100% di mata API
            self.bet_value = self.compute_bet_value_from_multiplier(self.multiplier, self.rule)
        else:
            self.sync_mode = "lock_multiplier"
            self.active_sync_mode = "lock_multiplier"

    def _reset_strategy_progression(self) -> None:
        self.fibonacci_index = 0
        self.paroli_step = 0
        self.dalembert_level = 0
        self.long_run_step = 0
        self.long_run_shield_remaining = 0
        self.mining_v2_step = 0
        self.mining_v2_cooldown_remaining = 0
        self.pro_safe_step = 0
        self.pro_recovery_step = 0
        self.pro_recovery_cooldown_remaining = 0
        self.pro_scalper_streak = 0
        self.premium_guard_step = 0
        self.premium_guard_cooldown_remaining = 0
        self.premium_compound_step = 0
        self.premium_step = 0
        self.premium_cooldown_remaining = 0

    def _reset_session_runtime(self) -> None:
        self.current_amount = self.base_amount
        self.total_profit = Decimal("0")
        self.bet_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.api_error_count = 0
        self.started_at = time.time()
        self._reset_strategy_progression()

    def _is_take_profit_reason(self, reason: str) -> bool:
        return reason in {"Mencapai target_profit", "Target harian premium tercapai"}

    def _is_stop_loss_reason(self, reason: str) -> bool:
        return reason in {"Mencapai stop_loss", "Batas rugi premium tercapai"}

    def _replay_reason_label(self, reason: str) -> str:
        if self._is_take_profit_reason(reason):
            return "take profit"
        if self._is_stop_loss_reason(reason):
            return "stop loss"
        return "reason"

    def _should_replay(self, reason: str) -> bool:
        if not self.simple_mode_enabled:
            return False
        if self.simple_replay_count <= 0:
            return False
        if self.simple_replay_done >= self.simple_replay_count:
            return False

        if self._is_take_profit_reason(reason):
            return self.simple_replay_on_take_profit
        if self._is_stop_loss_reason(reason):
            return self.simple_replay_on_stop_loss
        return False

    def _preset_prompt_entries(self) -> Tuple[Tuple[str, str], ...]:
        return (
            ("martingale", "Martingale"),
            ("fibonacci", "Fibonacci"),
            ("paroli", "Paroli"),
            ("anti_martingale", "Anti Martingale"),
            ("dalembert", "Dalembert"),
            ("flat", "Flat"),
            ("mining", "Mining"),
            ("mining_v2", "Mining V2"),
            ("pro_safe", "Pro Safe"),
            ("pro_recovery", "Pro Recovery"),
            ("", "Custom (no preset)"),
        )

    def prompt_preset_choice(self) -> None:
        if not self.simple_mode_enabled or not self.simple_preset_prompt:
            return
        if not sys.stdin.isatty():
            return

        current = self.preset_name if self.preset_enabled else "custom"
        entries = self._preset_prompt_entries()
        print(THEME_TEXT_DIM + "-" * 95)
        print(THEME_TEXT_BRIGHT + "PRESET CONFIRMATION")
        print(THEME_PRIMARY + f"Preset config saat ini: {current}")
        print(THEME_PRIMARY + "Pilih preset (Enter/0 = sesuai config):")
        for idx, (_, label) in enumerate(entries, start=1):
            print(THEME_TEXT + f" {idx}. {label}")

        try:
            raw_choice = input("Preset pilihan [0]: ").strip().lower()
        except EOFError:
            return

        if raw_choice in {"", "0", "config", "cfg"}:
            self.info("Preset tetap sesuai config.")
            return

        selected: str | None = None
        by_number = {str(i): key for i, (key, _) in enumerate(entries, start=1)}
        alias_map = {
            "fibinacci": "fibonacci",
            "anti-martingale": "anti_martingale",
            "pro-safe": "pro_safe",
            "pro-recovery": "pro_recovery",
            "pro-scalper": "pro_recovery",
            "premium-guard": "pro_safe",
            "premium-compound": "mining_v2",
            "premium": "pro_recovery",
        }
        if raw_choice in by_number:
            selected = by_number[raw_choice]
        else:
            if raw_choice in alias_map:
                selected = alias_map[raw_choice]
            for key, label in entries:
                label_key = label.lower().split(" (")[0].replace(" ", "_")
                if raw_choice in {key, label_key}:
                    selected = key
                    break

        if selected is None:
            self.warn("Pilihan preset tidak dikenali. Menggunakan preset sesuai config.")
            return

        self._reset_strategy_progression()
        self.current_amount = self.base_amount
        if selected:
            self.preset_enabled = True
            self.preset_name = selected
            self.simple_system = selected
            self.info(f"Preset runtime dipilih: {selected}")
        else:
            self.preset_enabled = False
            self.preset_name = ""
            self.simple_system = ""
            self.info("Preset runtime dipilih: custom (no preset)")

    def get_currency_balance(self) -> Decimal:
        data = self.client.get_balances()
        balances = data.get("balances", [])
        if not isinstance(balances, list):
            raise APIError("Format balances dari API tidak valid.")

        for item in balances:
            if not isinstance(item, dict):
                continue
            if str(item.get("currency", "")).lower() == self.currency:
                return to_decimal(item.get("amount", "0"), f"balance[{self.currency}]")

        available = [str(x.get("currency", "")).lower() for x in balances if isinstance(x, dict)]
        raise APIError(
            f"Currency '{self.currency}' tidak ditemukan di balance. Currency tersedia: {', '.join(available)}"
        )

    def random_client_seed(self, length: int = 24) -> str:
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(random.choice(alphabet) for _ in range(length))

    def persist_synced_pair(self, path: str = "config.json") -> None:
        if not self.save_synced_pair_to_config:
            return

        config_path = Path(path)
        if not config_path.exists():
            return

        try:
            raw_cfg = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        if not isinstance(raw_cfg, dict):
            return

        new_multiplier = float(self.multiplier)
        new_bet_value = float(self.bet_value)
        changed = False

        raw_simple = raw_cfg.get("simple")
        if isinstance(raw_simple, dict):
            try:
                raw_simple_enabled = parse_toggle(raw_simple.get("enabled", "OFF"), "simple.enabled")
            except ConfigError:
                raw_simple_enabled = False

            if raw_simple_enabled:
                if str(raw_simple.get("multiplier")) != str(new_multiplier):
                    raw_simple["multiplier"] = new_multiplier
                    changed = True
                for hidden_key in ("save_synced_pair_to_config", "last_synced_multiplier", "last_synced_chance"):
                    if hidden_key in raw_simple:
                        raw_simple.pop(hidden_key, None)
                        changed = True

        raw_bot = raw_cfg.get("bot")
        if isinstance(raw_bot, dict):
            if str(raw_bot.get("multiplier")) != str(new_multiplier):
                raw_bot["multiplier"] = new_multiplier
                changed = True
            if str(raw_bot.get("bet_value")) != str(new_bet_value):
                raw_bot["bet_value"] = new_bet_value
                changed = True
            if str(raw_bot.get("last_synced_multiplier")) != str(new_multiplier):
                raw_bot["last_synced_multiplier"] = new_multiplier
                changed = True
            if str(raw_bot.get("last_synced_bet_value")) != str(new_bet_value):
                raw_bot["last_synced_bet_value"] = new_bet_value
                changed = True

        if not changed:
            return

        try:
            config_path.write_text(json.dumps(raw_cfg, indent=2), encoding="utf-8")
        except OSError:
            return

    def maybe_refresh_seeds(self) -> None:
        if self.refresh_server_seed_every > 0 and self.bet_count % self.refresh_server_seed_every == 0:
            try:
                data = self.client.refresh_server_seed()
                server_hash = str(data.get("server_seed_hashed", "-"))
                self.info(f"Server seed refreshed: {server_hash}")
            except APIError as exc:
                self.warn(f"Gagal refresh server seed: {exc}")

        if self.refresh_client_seed_every > 0 and self.bet_count % self.refresh_client_seed_every == 0:
            seed = self.random_client_seed()
            try:
                data = self.client.refresh_client_seed(seed)
                new_seed = str(data.get("seed", seed))
                self.info(f"Client seed refreshed: {new_seed}")
            except APIError as exc:
                self.warn(f"Gagal refresh client seed: {exc}")

    def _fibonacci_value(self, index: int) -> int:
        while index >= len(self.fibonacci_cache):
            self.fibonacci_cache.append(self.fibonacci_cache[-1] + self.fibonacci_cache[-2])
        return self.fibonacci_cache[index]

    def _apply_rule_switch(self, outcome: str) -> None:
        if outcome == "win" and self.switch_rule_on_win:
            self.rule = "under" if self.rule == "over" else "over"
        elif outcome == "loss" and self.switch_rule_on_loss:
            self.rule = "under" if self.rule == "over" else "over"

    def _apply_custom_strategy(self, outcome: str) -> None:
        if outcome == "win":
            if self.custom_on_win_reset:
                self.current_amount = self.base_amount
            else:
                self.current_amount = (self.current_amount * self.custom_on_win_multiplier) + self.custom_on_win_addition
        else:
            if self.custom_on_loss_reset:
                self.current_amount = self.base_amount
            else:
                self.current_amount = (self.current_amount * self.custom_on_loss_multiplier) + self.custom_on_loss_addition

    def _apply_preset_strategy(self, outcome: str) -> None:
        if self.preset_name == "flat":
            self.current_amount = self.base_amount
            return

        if self.preset_name == "martingale":
            if outcome == "win":
                self.current_amount = self.base_amount
            else:
                self.current_amount = self.current_amount * self.preset_martingale_multiplier
            return

        if self.preset_name == "fibonacci":
            if outcome == "loss":
                self.fibonacci_index += 1
            else:
                self.fibonacci_index = max(0, self.fibonacci_index - self.preset_fibonacci_step_back_on_win)
            fib_value = Decimal(str(self._fibonacci_value(self.fibonacci_index)))
            self.current_amount = self.base_amount * self.preset_fibonacci_unit * fib_value
            return

        if self.preset_name in {"paroli", "anti_martingale"}:
            if outcome == "win":
                self.paroli_step += 1
                if self.paroli_step >= self.preset_paroli_max_win_streak:
                    self.paroli_step = 0
                    self.current_amount = self.base_amount
                else:
                    self.current_amount = self.current_amount * self.preset_paroli_multiplier
            else:
                self.paroli_step = 0
                self.current_amount = self.base_amount
            return

        if self.preset_name == "dalembert":
            if outcome == "loss":
                self.dalembert_level += 1
            else:
                self.dalembert_level = max(0, self.dalembert_level - 1)

            increment = self.base_amount * self.preset_dalembert_step * Decimal(str(self.dalembert_level))
            self.current_amount = self.base_amount + increment
            return

        if self.preset_name in {"mining", "long_run_guard", "anti_losstrack"}:
            if self.long_run_shield_remaining > 0:
                if outcome == "loss":
                    self.long_run_step = min(self.preset_long_run_max_steps, self.long_run_step + 1)
                else:
                    self.long_run_step = max(0, self.long_run_step - self.preset_long_run_recovery_steps_on_win)
                self.current_amount = self.base_amount
                self.long_run_shield_remaining -= 1
                return

            if outcome == "loss":
                self.long_run_step = min(self.preset_long_run_max_steps, self.long_run_step + 1)
                shield_triggered = (
                    self.preset_long_run_shield_after_losses > 0
                    and self.consecutive_losses >= self.preset_long_run_shield_after_losses
                    and self.preset_long_run_shield_rounds > 0
                )
                if shield_triggered:
                    self.current_amount = self.base_amount
                    self.long_run_shield_remaining = max(0, self.preset_long_run_shield_rounds - 1)
                    return
            else:
                self.long_run_step = max(0, self.long_run_step - self.preset_long_run_recovery_steps_on_win)

            scale = self.preset_long_run_loss_multiplier ** self.long_run_step
            if scale > self.preset_long_run_max_scale:
                scale = self.preset_long_run_max_scale
            self.current_amount = self.base_amount * scale
            return

        if self.preset_name == "mining_v2":
            if self.mining_v2_cooldown_remaining > 0:
                if outcome == "win":
                    self.mining_v2_step = max(0, self.mining_v2_step - self.preset_mining_v2_recovery_steps_on_win)
                elif outcome == "loss":
                    self.mining_v2_step = min(self.preset_mining_v2_max_steps, self.mining_v2_step + 1)
                self.current_amount = self.base_amount
                self.mining_v2_cooldown_remaining -= 1
                return

            if outcome == "loss":
                self.mining_v2_step = min(self.preset_mining_v2_max_steps, self.mining_v2_step + 1)
                if (
                    self.preset_mining_v2_cooldown_trigger_losses > 0
                    and self.consecutive_losses >= self.preset_mining_v2_cooldown_trigger_losses
                    and self.preset_mining_v2_cooldown_rounds > 0
                ):
                    self.mining_v2_cooldown_remaining = self.preset_mining_v2_cooldown_rounds
                    self.current_amount = self.base_amount
                    return
            else:
                self.mining_v2_step = max(0, self.mining_v2_step - self.preset_mining_v2_recovery_steps_on_win)

            scale = self.preset_mining_v2_loss_multiplier ** self.mining_v2_step
            if scale > self.preset_mining_v2_max_scale:
                scale = self.preset_mining_v2_max_scale
            self.current_amount = self.base_amount * scale
            return

        if self.preset_name == "pro_safe":
            if outcome == "loss":
                self.pro_safe_step = min(self.preset_pro_safe_max_steps, self.pro_safe_step + 1)
            else:
                self.pro_safe_step = max(0, self.pro_safe_step - self.preset_pro_safe_recovery_steps_on_win)

            scale = self.preset_pro_safe_loss_multiplier ** self.pro_safe_step
            if scale > self.preset_pro_safe_max_scale:
                scale = self.preset_pro_safe_max_scale
            self.current_amount = self.base_amount * scale
            return

        if self.preset_name == "pro_recovery":
            if self.pro_recovery_cooldown_remaining > 0:
                if outcome == "win":
                    self.pro_recovery_step = max(
                        0, self.pro_recovery_step - self.preset_pro_recovery_recovery_steps_on_win
                    )
                elif outcome == "loss":
                    self.pro_recovery_step = min(self.preset_pro_recovery_max_steps, self.pro_recovery_step + 1)
                self.current_amount = self.base_amount
                self.pro_recovery_cooldown_remaining -= 1
                return

            if outcome == "loss":
                self.pro_recovery_step = min(self.preset_pro_recovery_max_steps, self.pro_recovery_step + 1)
                if (
                    self.preset_pro_recovery_cooldown_trigger_losses > 0
                    and self.consecutive_losses >= self.preset_pro_recovery_cooldown_trigger_losses
                    and self.preset_pro_recovery_cooldown_rounds > 0
                ):
                    self.pro_recovery_cooldown_remaining = self.preset_pro_recovery_cooldown_rounds
                    self.current_amount = self.base_amount
                    return
            else:
                self.pro_recovery_step = max(
                    0, self.pro_recovery_step - self.preset_pro_recovery_recovery_steps_on_win
                )

            scale = self.preset_pro_recovery_loss_multiplier ** self.pro_recovery_step
            if scale > self.preset_pro_recovery_max_scale:
                scale = self.preset_pro_recovery_max_scale
            self.current_amount = self.base_amount * scale
            return

        if self.preset_name == "pro_scalper":
            if outcome == "win":
                self.pro_scalper_streak += 1
                if self.pro_scalper_streak >= self.preset_pro_scalper_max_win_streak:
                    self.pro_scalper_streak = 0
                    self.current_amount = self.base_amount
                else:
                    self.current_amount = self.current_amount * self.preset_pro_scalper_win_multiplier
            else:
                self.pro_scalper_streak = 0
                self.current_amount = self.base_amount
            return

        if self.preset_name == "premium_guard":
            if self.current_balance <= Decimal("0"):
                self.current_amount = self.base_amount
                return

            if self.premium_guard_cooldown_remaining > 0:
                if outcome == "loss":
                    self.premium_guard_step = min(self.preset_premium_guard_max_steps, self.premium_guard_step + 1)
                elif outcome == "win":
                    self.premium_guard_step = max(0, self.premium_guard_step - 1)
                self.current_amount = self.base_amount
                self.premium_guard_cooldown_remaining -= 1
                return

            if outcome == "loss":
                self.premium_guard_step = min(self.preset_premium_guard_max_steps, self.premium_guard_step + 1)
                if (
                    self.preset_premium_guard_cooldown_trigger_losses > 0
                    and self.consecutive_losses >= self.preset_premium_guard_cooldown_trigger_losses
                    and self.preset_premium_guard_cooldown_rounds > 0
                ):
                    self.premium_guard_cooldown_remaining = self.preset_premium_guard_cooldown_rounds
                    self.current_amount = self.base_amount
                    return
            else:
                self.premium_guard_step = max(0, self.premium_guard_step - 1)

            scale = self.preset_premium_guard_loss_multiplier ** self.premium_guard_step
            if scale > self.preset_premium_guard_max_scale:
                scale = self.preset_premium_guard_max_scale
            scaled_amount = self.base_amount * scale
            risk_cap_amount = self.current_balance * self.preset_premium_guard_risk_percent / Decimal("100")
            if risk_cap_amount > Decimal("0"):
                scaled_amount = min(scaled_amount, risk_cap_amount)
            self.current_amount = max(self.base_amount, scaled_amount)
            return

        if self.preset_name == "premium_compound":
            if outcome == "loss":
                self.premium_compound_step = min(
                    self.preset_premium_compound_max_steps, self.premium_compound_step + 1
                )
            else:
                self.premium_compound_step = max(
                    0, self.premium_compound_step - self.preset_premium_compound_recovery_steps_on_win
                )

            scale = self.preset_premium_compound_loss_multiplier ** self.premium_compound_step
            boost_scale = Decimal("1")
            if (
                self.start_balance > Decimal("0")
                and self.total_profit > Decimal("0")
                and self.preset_premium_compound_profit_boost_percent > Decimal("0")
            ):
                boost_scale += (
                    (self.total_profit / self.start_balance)
                    * self.preset_premium_compound_profit_boost_percent
                    / Decimal("100")
                )
            scale = scale * boost_scale
            if scale > self.preset_premium_compound_max_scale:
                scale = self.preset_premium_compound_max_scale
            self.current_amount = self.base_amount * scale
            return

        if self.preset_name == "premium":
            if self.current_balance <= Decimal("0"):
                self.current_amount = self.base_amount
                return

            if self.premium_cooldown_remaining > 0:
                if outcome == "loss":
                    self.premium_step = min(self.preset_premium_max_steps, self.premium_step + 1)
                elif outcome == "win":
                    self.premium_step = max(0, self.premium_step - self.preset_premium_recovery_steps_on_win)
                self.current_amount = self.base_amount
                self.premium_cooldown_remaining -= 1
                return

            if outcome == "loss":
                self.premium_step = min(self.preset_premium_max_steps, self.premium_step + 1)
                if (
                    self.preset_premium_cooldown_trigger_losses > 0
                    and self.consecutive_losses >= self.preset_premium_cooldown_trigger_losses
                    and self.preset_premium_cooldown_rounds > 0
                ):
                    self.premium_cooldown_remaining = self.preset_premium_cooldown_rounds
                    self.current_amount = self.base_amount
                    return
            else:
                self.premium_step = max(0, self.premium_step - self.preset_premium_recovery_steps_on_win)

            scale = self.preset_premium_loss_multiplier ** self.premium_step
            if scale > self.preset_premium_max_scale:
                scale = self.preset_premium_max_scale

            scaled_amount = self.base_amount * scale

            risk_percent = self.preset_premium_risk_percent * scale
            if risk_percent > self.preset_premium_max_risk_percent:
                risk_percent = self.preset_premium_max_risk_percent
            risk_cap_amount = self.current_balance * risk_percent / Decimal("100")

            target_cap_amount = scaled_amount
            if self.premium_target_profit_abs > Decimal("0"):
                remaining_target = self.premium_target_profit_abs - self.total_profit
                if remaining_target > Decimal("0") and self.multiplier > Decimal("1"):
                    amount_to_target = remaining_target / (self.multiplier - Decimal("1"))
                    if amount_to_target > Decimal("0"):
                        target_cap_amount = min(target_cap_amount, amount_to_target)

            capped_amount = scaled_amount
            if risk_cap_amount > Decimal("0"):
                capped_amount = min(capped_amount, risk_cap_amount)
            capped_amount = min(capped_amount, target_cap_amount)
            self.current_amount = max(self.base_amount, capped_amount)
            return

        raise ConfigError(f"Preset strategy '{self.preset_name}' belum didukung.")

    def apply_strategy(self, outcome: str) -> None:
        self._apply_rule_switch(outcome)
        if self.preset_enabled:
            self._apply_preset_strategy(outcome)
        else:
            self._apply_custom_strategy(outcome)

        self.current_amount = self._normalize_amount(self.current_amount)

        if self.current_amount <= Decimal("0"):
            raise ConfigError("Nilai current_amount <= 0 setelah strategi. Cek strategy.on_win/on_loss.")

        self.sync_bet_pair()

    def stop_reason(self) -> str:
        if self.max_bets > 0 and self.bet_count >= self.max_bets:
            return "Mencapai max_bets"
        if self.preset_enabled and self.preset_name == "premium":
            if self.premium_target_profit_abs > 0 and self.total_profit >= self.premium_target_profit_abs:
                return "Target harian premium tercapai"
            if self.premium_stop_loss_abs > 0 and self.total_profit <= -self.premium_stop_loss_abs:
                return "Batas rugi premium tercapai"
        if self.target_profit > 0 and self.total_profit >= self.target_profit:
            return "Mencapai target_profit"
        if self.stop_loss > 0 and self.total_profit <= -self.stop_loss:
            return "Mencapai stop_loss"
        if self.stop_on_balance_below > 0 and self.current_balance <= self.stop_on_balance_below:
            return "Balance menyentuh stop_on_balance_below"
        if self.max_consecutive_losses > 0 and self.consecutive_losses >= self.max_consecutive_losses:
            return "Mencapai max_consecutive_losses"
        if self.max_consecutive_wins > 0 and self.consecutive_wins >= self.max_consecutive_wins:
            return "Mencapai max_consecutive_wins"
        if self.max_amount > 0 and self.current_amount > self.max_amount:
            return "Current amount melebihi max_amount"
        return ""

    def print_run_config(self) -> None:
        self.info("Koneksi API berhasil.")
        self.info(f"Currency     : {self.currency}")
        self.info(f"Rule         : {self.rule}")
        self.info(f"Base amount  : {format_decimal(self.base_amount, self.coin_decimal_places)}")
        self.info(f"Bet value    : {format_decimal(self.bet_value)}")
        self.info(f"Multiplier   : {format_decimal(self.multiplier)}")
        self.info(f"Sync mode    : {self.sync_mode} -> {self._effective_sync_mode()}")
        self.info(f"History style: {self.history_style}")
        self.info(f"Balance mode : {self.balance_sync_mode}")
        self.info(f"Coin digits  : {self.coin_decimal_places}")
        if self.show_idr_value:
            if self.idr_price > 0:
                self.info(
                    f"IDR value    : ON | {self._format_rupiah(self.idr_price)}/{self.currency_display} "
                    f"(upd {self.idr_last_update_at})"
                )
            else:
                self.info(f"IDR value    : ON | status={self.idr_status}")
        elif self.idr_status == "UNSUPPORTED":
            self.info(f"IDR value    : OFF | coin '{self.currency}' belum didukung source harga.")
        else:
            self.info("IDR value    : OFF")
        self.info(f"Sticky stats : {'ON' if self.sticky_footer_enabled else 'OFF'}")
        self.info(f"Config mode  : {'simple' if self.simple_mode_enabled else 'advanced'}")
        if self.simple_mode_enabled:
            win_inc_pct = (self.custom_on_win_multiplier - Decimal("1")) * Decimal("100")
            loss_inc_pct = (self.custom_on_loss_multiplier - Decimal("1")) * Decimal("100")
            system_name = self.preset_name if self.preset_enabled else "custom"
            self.info(
                "Simple cfg  : "
                f"system={system_name} "
                f"hilo_random={to_on_off(self.simple_hilo_random)} "
                f"hilo_fixed={'LOW' if self.simple_fixed_rule == 'under' else 'HI'} "
                f"chance_random={to_on_off(self.simple_chance_random_enabled)} "
                f"reset_win={to_on_off(self.custom_on_win_reset)} "
                f"reset_loss={to_on_off(self.custom_on_loss_reset)} "
                f"inc_win={format_decimal(win_inc_pct, 2)}% "
                f"inc_loss={format_decimal(loss_inc_pct, 2)}%"
            )
            if self.simple_chance_random_enabled:
                self.info(
                    "Chance rnd  : "
                    f"{format_decimal(self.simple_chance_random_min, 2)}%-"
                    f"{format_decimal(self.simple_chance_random_max, 2)}% "
                    f"prec={self.simple_chance_random_precision}"
                )
            self.info(
                "Replay cfg  : "
                f"TP={to_on_off(self.simple_replay_on_take_profit)} "
                f"SL={to_on_off(self.simple_replay_on_stop_loss)} "
                f"after={self.simple_replay_after_sec}s "
                f"count={self.simple_replay_count}"
            )
        preset_state = "ON" if self.preset_enabled else "OFF"
        self.info(f"Preset mode  : {preset_state}")
        if self.preset_enabled:
            self.info(f"Preset name  : {self.preset_name}")
            if self.preset_name in {"mining", "long_run_guard", "anti_losstrack"}:
                self.info(
                    "Mining cfg  : "
                    f"loss_x{format_decimal(self.preset_long_run_loss_multiplier, 4)} "
                    f"steps={self.preset_long_run_max_steps} "
                    f"recover={self.preset_long_run_recovery_steps_on_win} "
                    f"max_scale={format_decimal(self.preset_long_run_max_scale, 4)} "
                    f"shield={self.preset_long_run_shield_after_losses}/{self.preset_long_run_shield_rounds}"
                )
                self.warn("Mining note : mode ini menekan risiko streak, tapi tidak bisa menjamin anti-loss 100%.")
            if self.preset_name == "mining_v2":
                self.info(
                    "MiningV2 cfg: "
                    f"loss_x{format_decimal(self.preset_mining_v2_loss_multiplier, 4)} "
                    f"steps={self.preset_mining_v2_max_steps} "
                    f"recover={self.preset_mining_v2_recovery_steps_on_win} "
                    f"max_scale={format_decimal(self.preset_mining_v2_max_scale, 4)} "
                    f"cooldown={self.preset_mining_v2_cooldown_trigger_losses}/{self.preset_mining_v2_cooldown_rounds}"
                )
                self.warn("MiningV2 note: versi lebih halus untuk run panjang, tetap tidak menjamin anti-loss 100%.")
            if self.preset_name == "pro_safe":
                self.info(
                    "ProSafe cfg : "
                    f"loss_x{format_decimal(self.preset_pro_safe_loss_multiplier, 4)} "
                    f"steps={self.preset_pro_safe_max_steps} "
                    f"recover={self.preset_pro_safe_recovery_steps_on_win} "
                    f"max_scale={format_decimal(self.preset_pro_safe_max_scale, 4)}"
                )
            if self.preset_name == "pro_recovery":
                self.info(
                    "ProReco cfg : "
                    f"loss_x{format_decimal(self.preset_pro_recovery_loss_multiplier, 4)} "
                    f"steps={self.preset_pro_recovery_max_steps} "
                    f"recover={self.preset_pro_recovery_recovery_steps_on_win} "
                    f"max_scale={format_decimal(self.preset_pro_recovery_max_scale, 4)} "
                    f"cooldown={self.preset_pro_recovery_cooldown_trigger_losses}/"
                    f"{self.preset_pro_recovery_cooldown_rounds}"
                )
            if self.preset_name == "pro_scalper":
                self.info(
                    "ProScalp cfg: "
                    f"win_x{format_decimal(self.preset_pro_scalper_win_multiplier, 4)} "
                    f"max_streak={self.preset_pro_scalper_max_win_streak}"
                )
            if self.preset_name == "premium_guard":
                self.info(
                    "PremGuard cfg: "
                    f"loss_x{format_decimal(self.preset_premium_guard_loss_multiplier, 4)} "
                    f"steps={self.preset_premium_guard_max_steps} "
                    f"max_scale={format_decimal(self.preset_premium_guard_max_scale, 4)} "
                    f"risk={format_decimal(self.preset_premium_guard_risk_percent, 4)}% "
                    f"cooldown={self.preset_premium_guard_cooldown_trigger_losses}/"
                    f"{self.preset_premium_guard_cooldown_rounds}"
                )
            if self.preset_name == "premium_compound":
                self.info(
                    "PremComp cfg: "
                    f"loss_x{format_decimal(self.preset_premium_compound_loss_multiplier, 4)} "
                    f"steps={self.preset_premium_compound_max_steps} "
                    f"recover={self.preset_premium_compound_recovery_steps_on_win} "
                    f"max_scale={format_decimal(self.preset_premium_compound_max_scale, 4)} "
                    f"boost={format_decimal(self.preset_premium_compound_profit_boost_percent, 2)}%"
                )
            if self.preset_name == "premium":
                self.info(
                    "Premium cfg : "
                    f"target={format_decimal(self.preset_premium_daily_target_percent, 2)}% "
                    f"stop_loss={format_decimal(self.preset_premium_stop_loss_percent, 2)}% "
                    f"risk={format_decimal(self.preset_premium_risk_percent, 4)}%-"
                    f"{format_decimal(self.preset_premium_max_risk_percent, 4)}% "
                    f"loss_x{format_decimal(self.preset_premium_loss_multiplier, 4)} "
                    f"steps={self.preset_premium_max_steps} "
                    f"recover={self.preset_premium_recovery_steps_on_win} "
                    f"max_scale={format_decimal(self.preset_premium_max_scale, 4)} "
                    f"cooldown={self.preset_premium_cooldown_trigger_losses}/"
                    f"{self.preset_premium_cooldown_rounds}"
                )
                self.info(
                    f"Premium tgt : +{format_decimal(self.premium_target_profit_abs, self.coin_decimal_places)} "
                    f"{self.currency_display} / "
                    f"-{format_decimal(self.premium_stop_loss_abs, self.coin_decimal_places)} {self.currency_display}"
                )
                self.warn("Premium note: target harian adalah batas sesi, bukan jaminan profit tanpa loss.")
        if self.base_amount_before_normalize != self.base_amount:
            self.warn(
                f"Base amount dinormalisasi ke {format_decimal(self.base_amount, self.coin_decimal_places)} "
                f"{self.currency_display} sesuai batas desimal coin."
            )
        self.info(f"Delay        : {self.delay_seconds}s")
        self.info(f"Start balance: {format_decimal(self.start_balance, self.coin_decimal_places)} {self.currency_display}")
        self._emit_runtime_line(THEME_TEXT_DIM + "-" * 95)

    def summary(self) -> None:
        if self._sticky_region_active:
            sys.stdout.write("\x1b[r")  # Reset scroll region
            try:
                # Pindah cursor ke area footer dan hapus sisa footer agar summary bersih
                size = shutil.get_terminal_size(fallback=(120, 30))
                start_line = max(1, size.lines - self.sticky_footer_lines + 1)
                sys.stdout.write(f"\x1b[{start_line};1H")
                sys.stdout.write("\x1b[J")  # Clear to end of screen
            except Exception:
                pass
            sys.stdout.flush()
            self._sticky_region_active = False
        else:
            print("")

        runtime = int(time.time() - self.started_at)
        sign = "+" if self.total_profit >= 0 else ""
        print(THEME_TEXT_DIM + "-" * 95)
        print(THEME_TEXT_BRIGHT + "SESSION SUMMARY")
        print(THEME_PRIMARY + f"Durasi                : {runtime}s")
        print(THEME_PRIMARY + f"Total bet             : {self.bet_count}")
        print(THEME_PRIMARY + f"Win                   : {self.win_count}")
        print(THEME_SECONDARY + f"Loss                  : {self.loss_count}")
        print(THEME_PRIMARY + f"Start balance         : {format_decimal(self.start_balance, self.coin_decimal_places)} {self.currency_display}")
        print(
            THEME_PRIMARY
            + f"Final balance         : {format_decimal(self.current_balance, self.coin_decimal_places)} "
            f"{self.currency_display} ({self.balance_source})"
        )
        print(THEME_PRIMARY + f"API balance last      : {format_decimal(self.api_balance, self.coin_decimal_places)} {self.currency_display}")
        print(THEME_PRIMARY + f"Estimated balance     : {format_decimal(self.estimated_balance, self.coin_decimal_places)} {self.currency_display}")
        if self.show_idr_value and self.idr_price > 0:
            print(THEME_PRIMARY + f"IDR price             : {self._format_rupiah(self.idr_price)} / {self.currency_display}")
            print(
                THEME_PRIMARY
                + f"Final balance (IDR)   : {self._format_rupiah(self.current_balance * self.idr_price)}"
            )
        color = THEME_PRIMARY_BRIGHT if self.total_profit >= 0 else THEME_SECONDARY_BRIGHT
        print(color + f"Total profit/loss     : {sign}{format_decimal(self.total_profit, self.coin_decimal_places)} {self.currency_display}")
        if self.show_idr_value and self.idr_price > 0:
            idr_color = THEME_PRIMARY_BRIGHT if self.total_profit >= 0 else THEME_SECONDARY_BRIGHT
            print(idr_color + f"Total profit/loss IDR : {self._format_rupiah(self.total_profit * self.idr_price, signed=True)}")
        print(THEME_TEXT_DIM + "-" * 95)

    def run(self) -> None:
        abort_all = False
        self.prompt_preset_choice()

        while True:
            self._reset_session_runtime()
            session_stop_reason = ""

            try:
                self.start_balance = self.get_currency_balance()
                self.api_balance = self.start_balance
                self.estimated_balance = self.start_balance
                self.current_balance = self.start_balance
                if self.preset_enabled and self.preset_name == "premium":
                    self.premium_target_profit_abs = (
                        self.start_balance * self.preset_premium_daily_target_percent / Decimal("100")
                    )
                    self.premium_stop_loss_abs = (
                        self.start_balance * self.preset_premium_stop_loss_percent / Decimal("100")
                    )
                self._update_last_bet_snapshot(
                    state="wait",
                    amount=self.current_amount,
                    result_value="-",
                    profit=Decimal("0"),
                )
                self._refresh_idr_price(force=True)
                self.print_run_config()
                if self.history_style == "classic":
                    self._print_history_header()

                while True:
                    self.current_amount = self._normalize_amount(self.current_amount)
                    reason = self.stop_reason()
                    if reason:
                        session_stop_reason = reason
                        self.warn(f"Stop: {reason}")
                        break

                    if self.current_amount > self.current_balance:
                        session_stop_reason = "Current amount melebihi current balance"
                        self.warn(
                            f"Stop: amount {format_decimal(self.current_amount, self.coin_decimal_places)} lebih besar dari balance "
                            f"{format_decimal(self.current_balance, self.coin_decimal_places)}."
                        )
                        break

                    try:
                        self._apply_simple_runtime_controls_before_bet()
                        self.sync_bet_pair()
                        response = self.client.place_dice_bet(
                            currency=self.currency,
                            amount=self.current_amount,
                            rule=self.rule,
                            multiplier=self.multiplier,
                            bet_value=self.bet_value,
                        )
                        self.api_error_count = 0
                    except APIError as exc:
                        self.api_error_count += 1
                        self.error(f"API Error: {exc}")
                        err_lower = str(exc).lower()
                        if "amount scale is too high" in err_lower:
                            old_amount = self.current_amount
                            self.current_amount = self._normalize_amount(self.current_amount)
                            self.warn(
                                f"Amount dinormalisasi dari {format_decimal(old_amount, 16)} ke "
                                f"{format_decimal(self.current_amount, self.coin_decimal_places)} {self.currency_display}."
                            )
                            self.api_error_count = 0
                        if "incorrect win chance given" in str(exc).lower():
                            self.warn("Deteksi mismatch multiplier/bet_value. Sinkronisasi otomatis lock_multiplier.")
                            self.sync_mode = "lock_multiplier"
                            self.active_sync_mode = "lock_multiplier"
                            try:
                                self.sync_bet_pair()
                                self.api_error_count = 0
                                self.info(
                                    f"Pair baru => rule {self.rule} | bet_value {format_decimal(self.bet_value)} "
                                    f"| multiplier {format_decimal(self.multiplier, self.multiplier_precision)}"
                                )
                            except ConfigError as sync_exc:
                                session_stop_reason = f"Sinkronisasi gagal: {sync_exc}"
                                self.error(f"Gagal sinkronisasi pair: {sync_exc}")
                                break

                        if (not self.continue_on_api_error) or self.api_error_count > self.max_api_errors:
                            session_stop_reason = "Batas API error tercapai"
                            self.warn("Stop: batas API error tercapai.")
                            break
                        self.warn(f"Retry loop berikutnya setelah {self.delay_seconds}s ...")
                        time.sleep(self.delay_seconds)
                        continue

                    bet = response.get("bet", {})
                    user_balance = response.get("user_balance", {})

                    state = str(bet.get("state", "")).lower()
                    profit = to_decimal(bet.get("profit", "0"), "bet.profit")
                    result_value = str(bet.get("result_value", "-"))
                    self.total_profit += profit
                    self.bet_count += 1

                    if state == "win":
                        self.win_count += 1
                        self.consecutive_wins += 1
                        self.consecutive_losses = 0
                        state_color = THEME_PRIMARY
                    elif state == "loss":
                        self.loss_count += 1
                        self.consecutive_losses += 1
                        self.consecutive_wins = 0
                        state_color = THEME_SECONDARY
                    else:
                        self.warn("State bet tidak dikenali, dianggap loss untuk safety.")
                        self.loss_count += 1
                        self.consecutive_losses += 1
                        self.consecutive_wins = 0
                        state = "loss"
                        state_color = THEME_SECONDARY

                    self._update_balances(user_balance, profit)
                    self._refresh_balance_periodically()
                    self._refresh_idr_price()

                    self._update_last_bet_snapshot(
                        state=state,
                        amount=self.current_amount,
                        result_value=result_value,
                        profit=profit,
                    )

                    if self.history_style == "classic":
                        log_line = self._history_line(
                            state=state,
                            amount=self.current_amount,
                            result_value=result_value,
                            profit=profit,
                        )
                        self._emit_runtime_line(state_color + log_line)
                        if self.history_header_every > 0 and self.bet_count % self.history_header_every == 0:
                            self._print_history_header()
                    else:
                        self._print_mining_log(
                            state=state,
                            amount=self.current_amount,
                            result_value=result_value,
                            profit=profit,
                        )

                    try:
                        self.apply_strategy(state)
                    except ConfigError as exc:
                        session_stop_reason = f"Strategi error: {exc}"
                        self.error(f"Strategi error: {exc}")
                        break

                    self.maybe_refresh_seeds()
                    time.sleep(self.delay_seconds)
            except KeyboardInterrupt:
                abort_all = True
                session_stop_reason = "Stop: dihentikan oleh user (Ctrl+C)."
                self.warn(session_stop_reason)
            except APIError as exc:
                session_stop_reason = f"Gagal start sesi: {exc}"
                self.error(session_stop_reason)
            finally:
                self.summary()

            if abort_all:
                break

            if self._should_replay(session_stop_reason):
                self.simple_replay_done += 1
                replay_label = self._replay_reason_label(session_stop_reason)
                self.warn(
                    f"Replay {replay_label} {self.simple_replay_done}/{self.simple_replay_count} "
                    f"dalam {self.simple_replay_after_sec}s ..."
                )
                time.sleep(self.simple_replay_after_sec)
                continue

            break


def validate_config(cfg: Dict[str, Any]) -> None:
    if not isinstance(cfg, dict):
        raise ConfigError("Isi config.json harus object JSON.")

    required_top = ["api", "bot", "strategy", "display"]
    for key in required_top:
        if key not in cfg:
            raise ConfigError(f"Key '{key}' tidak ada di config.")

    token = str(cfg["api"].get("token", "")).strip()
    if not token or "PASTE_WOLFBET_API_TOKEN" in token:
        raise ConfigError("Isi api.token di config.json dengan API token dari Wolfbet.")

    base_amount = to_decimal(cfg["bot"].get("base_amount"), "bot.base_amount")
    if base_amount <= 0:
        raise ConfigError("bot.base_amount harus > 0.")

    bet_value = to_decimal(cfg["bot"].get("bet_value"), "bot.bet_value")
    if bet_value <= 0 or bet_value >= Decimal("99.99"):
        raise ConfigError("bot.bet_value harus > 0 dan < 99.99.")

    auto_multiplier = parse_toggle(cfg["bot"].get("auto_multiplier", "OFF"), "bot.auto_multiplier")
    sync_mode = str(cfg["bot"].get("sync_mode", "auto")).lower()
    if sync_mode not in {"auto", "lock_multiplier", "lock_bet_value", "none"}:
        raise ConfigError("bot.sync_mode harus: auto, lock_multiplier, lock_bet_value, atau none.")

    sync_fallback_mode = str(cfg["bot"].get("sync_fallback_mode", "lock_multiplier")).lower()
    if sync_fallback_mode not in {"lock_multiplier", "lock_bet_value", "none"}:
        raise ConfigError("bot.sync_fallback_mode harus: lock_multiplier, lock_bet_value, atau none.")

    multiplier_precision = int(cfg["bot"].get("multiplier_precision", 4))
    if multiplier_precision < 0 or multiplier_precision > 8:
        raise ConfigError("bot.multiplier_precision harus 0-8.")

    bet_value_precision = int(cfg["bot"].get("bet_value_precision", 2))
    if bet_value_precision < 0 or bet_value_precision > 8:
        raise ConfigError("bot.bet_value_precision harus 0-8.")

    multiplier = to_decimal(cfg["bot"].get("multiplier"), "bot.multiplier")
    if (not auto_multiplier) and sync_mode in {"lock_multiplier", "none"} and multiplier <= 1:
        raise ConfigError("bot.multiplier harus > 1 jika auto_multiplier=OFF.")

    parse_toggle(cfg["bot"].get("save_synced_pair_to_config", "ON"), "bot.save_synced_pair_to_config")
    to_decimal(cfg["bot"].get("last_synced_multiplier", 0), "bot.last_synced_multiplier")
    to_decimal(cfg["bot"].get("last_synced_bet_value", 0), "bot.last_synced_bet_value")

    rule = str(cfg["bot"].get("rule", "")).lower()
    if rule not in {"under", "over"}:
        raise ConfigError("bot.rule harus 'under' atau 'over'.")

    delay_seconds = float(cfg["bot"].get("delay_seconds", 0))
    if delay_seconds < 0:
        raise ConfigError("bot.delay_seconds tidak boleh negatif.")

    parse_toggle(cfg["bot"].get("continue_on_api_error", "ON"), "bot.continue_on_api_error")

    strategy_cfg = cfg["strategy"]
    parse_toggle(strategy_cfg.get("switch_rule_on_win", "OFF"), "strategy.switch_rule_on_win")
    parse_toggle(strategy_cfg.get("switch_rule_on_loss", "OFF"), "strategy.switch_rule_on_loss")

    on_win_cfg = strategy_cfg.get("on_win", {})
    on_loss_cfg = strategy_cfg.get("on_loss", {})
    parse_toggle(on_win_cfg.get("reset_to_base", "ON"), "strategy.on_win.reset_to_base")
    parse_toggle(on_loss_cfg.get("reset_to_base", "OFF"), "strategy.on_loss.reset_to_base")

    on_win_multiplier = to_decimal(on_win_cfg.get("amount_multiplier", 1.0), "strategy.on_win.amount_multiplier")
    on_loss_multiplier = to_decimal(on_loss_cfg.get("amount_multiplier", 2.0), "strategy.on_loss.amount_multiplier")
    if on_win_multiplier < 0:
        raise ConfigError("strategy.on_win.amount_multiplier tidak boleh negatif.")
    if on_loss_multiplier < 0:
        raise ConfigError("strategy.on_loss.amount_multiplier tidak boleh negatif.")

    preset_cfg = strategy_cfg.get("preset", {})
    preset_enabled = parse_toggle(preset_cfg.get("enabled", "OFF"), "strategy.preset.enabled")
    selected_preset = resolve_selected_preset(preset_cfg, "strategy.preset")
    if preset_enabled and not selected_preset:
        raise ConfigError("strategy.preset.enabled=ON, tapi belum ada preset yang ON di strategy.preset.use.")

    if to_decimal(preset_cfg.get("martingale_multiplier", 2.0), "strategy.preset.martingale_multiplier") <= 0:
        raise ConfigError("strategy.preset.martingale_multiplier harus > 0.")
    if to_decimal(preset_cfg.get("fibonacci_unit", 1.0), "strategy.preset.fibonacci_unit") <= 0:
        raise ConfigError("strategy.preset.fibonacci_unit harus > 0.")
    if int(preset_cfg.get("fibonacci_step_back_on_win", 2)) < 0:
        raise ConfigError("strategy.preset.fibonacci_step_back_on_win tidak boleh negatif.")
    if to_decimal(preset_cfg.get("paroli_multiplier", 2.0), "strategy.preset.paroli_multiplier") <= 0:
        raise ConfigError("strategy.preset.paroli_multiplier harus > 0.")
    if int(preset_cfg.get("paroli_max_win_streak", 3)) < 1:
        raise ConfigError("strategy.preset.paroli_max_win_streak minimal 1.")
    if to_decimal(preset_cfg.get("dalembert_step", 1.0), "strategy.preset.dalembert_step") <= 0:
        raise ConfigError("strategy.preset.dalembert_step harus > 0.")
    if to_decimal(preset_cfg.get("long_run_loss_multiplier", 1.08), "strategy.preset.long_run_loss_multiplier") < 1:
        raise ConfigError("strategy.preset.long_run_loss_multiplier harus >= 1.")
    if int(preset_cfg.get("long_run_max_steps", 8)) < 0:
        raise ConfigError("strategy.preset.long_run_max_steps tidak boleh negatif.")
    if int(preset_cfg.get("long_run_recovery_steps_on_win", 2)) < 0:
        raise ConfigError("strategy.preset.long_run_recovery_steps_on_win tidak boleh negatif.")
    if to_decimal(preset_cfg.get("long_run_max_scale", 2.0), "strategy.preset.long_run_max_scale") < 1:
        raise ConfigError("strategy.preset.long_run_max_scale minimal 1.")
    if int(preset_cfg.get("long_run_shield_after_losses", 5)) < 0:
        raise ConfigError("strategy.preset.long_run_shield_after_losses tidak boleh negatif.")
    if int(preset_cfg.get("long_run_shield_rounds", 2)) < 0:
        raise ConfigError("strategy.preset.long_run_shield_rounds tidak boleh negatif.")
    if to_decimal(preset_cfg.get("mining_v2_loss_multiplier", 1.03), "strategy.preset.mining_v2_loss_multiplier") < 1:
        raise ConfigError("strategy.preset.mining_v2_loss_multiplier harus >= 1.")
    if int(preset_cfg.get("mining_v2_max_steps", 6)) < 0:
        raise ConfigError("strategy.preset.mining_v2_max_steps tidak boleh negatif.")
    if int(preset_cfg.get("mining_v2_recovery_steps_on_win", 3)) < 0:
        raise ConfigError("strategy.preset.mining_v2_recovery_steps_on_win tidak boleh negatif.")
    if to_decimal(preset_cfg.get("mining_v2_max_scale", 1.50), "strategy.preset.mining_v2_max_scale") < 1:
        raise ConfigError("strategy.preset.mining_v2_max_scale minimal 1.")
    if int(preset_cfg.get("mining_v2_cooldown_trigger_losses", 4)) < 0:
        raise ConfigError("strategy.preset.mining_v2_cooldown_trigger_losses tidak boleh negatif.")
    if int(preset_cfg.get("mining_v2_cooldown_rounds", 2)) < 0:
        raise ConfigError("strategy.preset.mining_v2_cooldown_rounds tidak boleh negatif.")
    if to_decimal(preset_cfg.get("pro_safe_loss_multiplier", 1.02), "strategy.preset.pro_safe_loss_multiplier") < 1:
        raise ConfigError("strategy.preset.pro_safe_loss_multiplier harus >= 1.")
    if int(preset_cfg.get("pro_safe_max_steps", 5)) < 0:
        raise ConfigError("strategy.preset.pro_safe_max_steps tidak boleh negatif.")
    if int(preset_cfg.get("pro_safe_recovery_steps_on_win", 2)) < 0:
        raise ConfigError("strategy.preset.pro_safe_recovery_steps_on_win tidak boleh negatif.")
    if to_decimal(preset_cfg.get("pro_safe_max_scale", 1.25), "strategy.preset.pro_safe_max_scale") < 1:
        raise ConfigError("strategy.preset.pro_safe_max_scale minimal 1.")
    if to_decimal(
        preset_cfg.get("pro_recovery_loss_multiplier", 1.06), "strategy.preset.pro_recovery_loss_multiplier"
    ) < 1:
        raise ConfigError("strategy.preset.pro_recovery_loss_multiplier harus >= 1.")
    if int(preset_cfg.get("pro_recovery_max_steps", 6)) < 0:
        raise ConfigError("strategy.preset.pro_recovery_max_steps tidak boleh negatif.")
    if int(preset_cfg.get("pro_recovery_recovery_steps_on_win", 1)) < 0:
        raise ConfigError("strategy.preset.pro_recovery_recovery_steps_on_win tidak boleh negatif.")
    if to_decimal(preset_cfg.get("pro_recovery_max_scale", 2.0), "strategy.preset.pro_recovery_max_scale") < 1:
        raise ConfigError("strategy.preset.pro_recovery_max_scale minimal 1.")
    if int(preset_cfg.get("pro_recovery_cooldown_trigger_losses", 4)) < 0:
        raise ConfigError("strategy.preset.pro_recovery_cooldown_trigger_losses tidak boleh negatif.")
    if int(preset_cfg.get("pro_recovery_cooldown_rounds", 2)) < 0:
        raise ConfigError("strategy.preset.pro_recovery_cooldown_rounds tidak boleh negatif.")
    if to_decimal(preset_cfg.get("pro_scalper_win_multiplier", 1.35), "strategy.preset.pro_scalper_win_multiplier") <= 1:
        raise ConfigError("strategy.preset.pro_scalper_win_multiplier harus > 1.")
    if int(preset_cfg.get("pro_scalper_max_win_streak", 3)) < 1:
        raise ConfigError("strategy.preset.pro_scalper_max_win_streak minimal 1.")
    if to_decimal(
        preset_cfg.get("premium_guard_loss_multiplier", 1.04), "strategy.preset.premium_guard_loss_multiplier"
    ) < 1:
        raise ConfigError("strategy.preset.premium_guard_loss_multiplier harus >= 1.")
    if int(preset_cfg.get("premium_guard_max_steps", 5)) < 0:
        raise ConfigError("strategy.preset.premium_guard_max_steps tidak boleh negatif.")
    if to_decimal(preset_cfg.get("premium_guard_max_scale", 1.40), "strategy.preset.premium_guard_max_scale") < 1:
        raise ConfigError("strategy.preset.premium_guard_max_scale minimal 1.")
    if to_decimal(preset_cfg.get("premium_guard_risk_percent", 0.03), "strategy.preset.premium_guard_risk_percent") <= 0:
        raise ConfigError("strategy.preset.premium_guard_risk_percent harus > 0.")
    if int(preset_cfg.get("premium_guard_cooldown_trigger_losses", 4)) < 0:
        raise ConfigError("strategy.preset.premium_guard_cooldown_trigger_losses tidak boleh negatif.")
    if int(preset_cfg.get("premium_guard_cooldown_rounds", 2)) < 0:
        raise ConfigError("strategy.preset.premium_guard_cooldown_rounds tidak boleh negatif.")
    if to_decimal(
        preset_cfg.get("premium_compound_loss_multiplier", 1.03), "strategy.preset.premium_compound_loss_multiplier"
    ) < 1:
        raise ConfigError("strategy.preset.premium_compound_loss_multiplier harus >= 1.")
    if int(preset_cfg.get("premium_compound_max_steps", 5)) < 0:
        raise ConfigError("strategy.preset.premium_compound_max_steps tidak boleh negatif.")
    if int(preset_cfg.get("premium_compound_recovery_steps_on_win", 2)) < 0:
        raise ConfigError("strategy.preset.premium_compound_recovery_steps_on_win tidak boleh negatif.")
    if to_decimal(
        preset_cfg.get("premium_compound_max_scale", 1.60), "strategy.preset.premium_compound_max_scale"
    ) < 1:
        raise ConfigError("strategy.preset.premium_compound_max_scale minimal 1.")
    if to_decimal(
        preset_cfg.get("premium_compound_profit_boost_percent", 15.0),
        "strategy.preset.premium_compound_profit_boost_percent",
    ) < 0:
        raise ConfigError("strategy.preset.premium_compound_profit_boost_percent tidak boleh negatif.")
    if to_decimal(
        preset_cfg.get("premium_daily_target_percent", 10),
        "strategy.preset.premium_daily_target_percent",
    ) < 0:
        raise ConfigError("strategy.preset.premium_daily_target_percent tidak boleh negatif.")
    if to_decimal(
        preset_cfg.get("premium_stop_loss_percent", 5),
        "strategy.preset.premium_stop_loss_percent",
    ) < 0:
        raise ConfigError("strategy.preset.premium_stop_loss_percent tidak boleh negatif.")
    premium_risk_percent = to_decimal(
        preset_cfg.get("premium_risk_percent", 0.05), "strategy.preset.premium_risk_percent"
    )
    premium_max_risk_percent = to_decimal(
        preset_cfg.get("premium_max_risk_percent", 0.25), "strategy.preset.premium_max_risk_percent"
    )
    if premium_risk_percent <= 0:
        raise ConfigError("strategy.preset.premium_risk_percent harus > 0.")
    if premium_max_risk_percent <= 0:
        raise ConfigError("strategy.preset.premium_max_risk_percent harus > 0.")
    if premium_max_risk_percent < premium_risk_percent:
        raise ConfigError("strategy.preset.premium_max_risk_percent harus >= premium_risk_percent.")
    if to_decimal(preset_cfg.get("premium_loss_multiplier", 1.06), "strategy.preset.premium_loss_multiplier") < 1:
        raise ConfigError("strategy.preset.premium_loss_multiplier harus >= 1.")
    if int(preset_cfg.get("premium_max_steps", 5)) < 0:
        raise ConfigError("strategy.preset.premium_max_steps tidak boleh negatif.")
    if int(preset_cfg.get("premium_recovery_steps_on_win", 2)) < 0:
        raise ConfigError("strategy.preset.premium_recovery_steps_on_win tidak boleh negatif.")
    if to_decimal(preset_cfg.get("premium_max_scale", 1.35), "strategy.preset.premium_max_scale") < 1:
        raise ConfigError("strategy.preset.premium_max_scale minimal 1.")
    if int(preset_cfg.get("premium_cooldown_trigger_losses", 4)) < 0:
        raise ConfigError("strategy.preset.premium_cooldown_trigger_losses tidak boleh negatif.")
    if int(preset_cfg.get("premium_cooldown_rounds", 2)) < 0:
        raise ConfigError("strategy.preset.premium_cooldown_rounds tidak boleh negatif.")

    if int(cfg["api"].get("retry_count", 0)) < 0:
        raise ConfigError("api.retry_count tidak boleh negatif.")

    if int(cfg["api"].get("rate_limit_wait_seconds", 0)) < 0:
        raise ConfigError("api.rate_limit_wait_seconds tidak boleh negatif.")

    history_style = str(cfg["display"].get("history_style", "mining")).lower()
    if history_style not in {"mining", "classic"}:
        raise ConfigError("display.history_style harus 'mining' atau 'classic'.")

    parse_toggle(cfg["display"].get("show_timestamp", "ON"), "display.show_timestamp")
    parse_toggle(cfg["display"].get("show_balance_each_bet", "ON"), "display.show_balance_each_bet")

    if int(cfg["display"].get("history_header_every", 20)) < 0:
        raise ConfigError("display.history_header_every tidak boleh negatif.")

    if int(cfg["display"].get("history_width", 0)) < 0:
        raise ConfigError("display.history_width tidak boleh negatif.")

    parse_toggle(cfg["display"].get("sticky_stats_footer", "ON"), "display.sticky_stats_footer")

    coin_decimal_places = int(cfg["display"].get("coin_decimal_places", 8))
    if coin_decimal_places < 0 or coin_decimal_places > 8:
        raise ConfigError("display.coin_decimal_places harus 0-8.")

    amount_display_precision = int(cfg["display"].get("amount_display_precision", 8))
    if amount_display_precision < 0 or amount_display_precision > 8:
        raise ConfigError("display.amount_display_precision harus 0-8.")
    if amount_display_precision > coin_decimal_places:
        raise ConfigError("display.amount_display_precision tidak boleh lebih besar dari display.coin_decimal_places.")

    profit_display_precision = int(cfg["display"].get("profit_display_precision", 8))
    if profit_display_precision < 0 or profit_display_precision > 8:
        raise ConfigError("display.profit_display_precision harus 0-8.")
    if profit_display_precision > coin_decimal_places:
        raise ConfigError("display.profit_display_precision tidak boleh lebih besar dari display.coin_decimal_places.")

    balance_display_precision = int(cfg["display"].get("balance_display_precision", 8))
    if balance_display_precision < 0 or balance_display_precision > 8:
        raise ConfigError("display.balance_display_precision harus 0-8.")
    if balance_display_precision > coin_decimal_places:
        raise ConfigError("display.balance_display_precision tidak boleh lebih besar dari display.coin_decimal_places.")

    balance_sync_mode = str(cfg["display"].get("balance_sync_mode", "hybrid")).lower()
    if balance_sync_mode not in {"hybrid", "api", "estimated"}:
        raise ConfigError("display.balance_sync_mode harus 'hybrid', 'api', atau 'estimated'.")

    if int(cfg["display"].get("balance_refresh_every", 20)) < 0:
        raise ConfigError("display.balance_refresh_every tidak boleh negatif.")

    parse_toggle(cfg["display"].get("show_idr_value", "OFF"), "display.show_idr_value")
    if int(cfg["display"].get("idr_refresh_seconds", 30)) < 0:
        raise ConfigError("display.idr_refresh_seconds tidak boleh negatif.")


def load_config(path: str) -> Dict[str, Any]:
    config_path = Path(path)
    defaults = default_config()
    user_template = default_user_config_template()

    if not config_path.exists() or config_path.stat().st_size == 0:
        config_path.write_text(json.dumps(user_template, indent=2), encoding="utf-8")
        raise ConfigError(
            f"{path} belum ada/masih kosong. Template config sudah dibuat, isi token lalu jalankan ulang."
        )

    try:
        user_cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Format JSON invalid di {path}: {exc}") from exc

    merged = deep_merge(defaults, user_cfg)
    apply_simple_settings(merged)
    validate_config(merged)
    return merged


def main() -> None:
    init(autoreset=True)
    print_banner()
    try:
        cfg = load_config("config.json")
        client = WolfbetClient(cfg)
        bot = DiceBot(cfg, client)
        bot.persist_synced_pair("config.json")
        bot.run()
    except ConfigError as exc:
        print(THEME_SECONDARY + f"[CONFIG] {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(THEME_SECONDARY + "\n[STOP] Dihentikan oleh user.")
        sys.exit(0)
    except Exception as exc:
        print(THEME_SECONDARY_BRIGHT + f"[FATAL] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
