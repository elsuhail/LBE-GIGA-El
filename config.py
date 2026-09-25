from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CardSpec:
    cost: int
    damage: int = 0
    energy_gain: int = 0
    draw_extra: int = 0
    greed: bool = False
    text: str = ""


@dataclass(frozen=True)
class GameBalance:
    target_hp_base: int = 30  # HP Target Stage 1
    target_hp_per_stage: int = 15  # tambahan HP tiap stage
    turn_limit: int = 3  # turn per stage
    energy_per_turn: int = 3  # energi di awal tiap turn (reset)
    starting_coins: int = 0
    coins_per_kill: int = 15  # koin tiap Target hancur
    greed_bonus: int = 15  # bonus koin jika kill via Greed
    draw_per_turn: int = 5
    max_hand: int = 10
    shop_card_price: int = 10
    remove_base_price: int = 5  # harga awal jasa hapus
    remove_price_step: int = 5  # kenaikan tiap dipakai
    min_deck_size: int = 5  # jasa hapus terkunci jika deck <= ini
    starter_deck: dict[str, int] = field(
        default_factory=lambda: {"Punch": 6, "Rest": 4}
    )
    shop_pool: tuple[str, ...] = (
        "Heavy Smash",
        "Double Strike",
        "Adrenaline",
        "Quick Jab",
        "Greed",
    )
    card_specs: dict[str, CardSpec] = field(
        default_factory=lambda: {
            "Punch": CardSpec(cost=1, damage=5, text="Damage 5"),
            "Rest": CardSpec(cost=0, text="Tanpa efek"),
            "Heavy Smash": CardSpec(cost=3, damage=25, text="Damage 25"),
            "Double Strike": CardSpec(cost=2, damage=12, text="Damage 12"),
            "Adrenaline": CardSpec(cost=0, energy_gain=2, text="+2 Energi"),
            "Quick Jab": CardSpec(
                cost=1, damage=3, draw_extra=1, text="Damage 3, tarik 1 kartu"
            ),
            "Greed": CardSpec(
                cost=1,
                damage=2,
                greed=True,
                text="Damage 2. +15 koin jika menghabisi",
            ),
        }
    )
    target_names: tuple[str, ...] = (
        "Tralalelo Tralala",
        "Bombini Gusini",
        "Ambalabu",
        "Br Br Patapim",
        "Kriuk Kriuk Nyos",
        "Mbembe be",
        "Tung Tung Sahur",
        "Kalkulus 1",
    )

    def target_max_hp(self, stage: int) -> int:
        # HP Target untuk stage tertentu (stage mulai dari 1).
        return self.target_hp_base + (stage - 1) * self.target_hp_per_stage

    def target_name(self, stage: int) -> str:
        # Nama kosmetik Target, berputar tiap stage.
        return self.target_names[(stage - 1) % len(self.target_names)]


@dataclass(frozen=True)
class AppSettings:
    width: int = 1920
    height: int = 1080
    fps: int = 60
    title: str = "Pukulin Aja"


BALANCE: GameBalance = GameBalance()
APP: AppSettings = AppSettings()

BLACK = (15, 15, 15)
PANEL_DARK = (30, 30, 36)
WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 250)

PINK = (255, 79, 163)
PINK_LIGHT = (255, 140, 198)
PINK_DARK = (194, 51, 122)

DISABLED_FILL = (74, 74, 94)
DISABLED_TEXT = (138, 138, 160)
