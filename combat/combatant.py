from dataclasses import dataclass, field
from typing import List, Optional
import random
import json
from enum import Enum
import json
import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List


# ===== ENUMS =====

class MovementType(Enum):
    WALK = "walk"
    FLY = "fly"
    SWIM = "swim"
    CLIMB = "climb"
    HOVER = "hover"
    BURROW = "burrow"


# ===== SPEED =====

class Speed:
    def __init__(self, **speeds: int):
        self.speeds = {movement: 0 for movement in MovementType}
        for key, value in speeds.items():
            if isinstance(key, MovementType):
                self.speeds[key] = value
            elif isinstance(key, str):
                try:
                    self.speeds[MovementType[key.upper()]] = value
                except KeyError:
                    raise ValueError(f"Unknown movement type: {key}")

    def get(self, movement_type: MovementType) -> int:
        return self.speeds.get(movement_type, 0)

    def to_dict(self) -> dict:
        return {
            movement.value: speed
            for movement, speed in self.speeds.items()
            if speed > 0
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str):
        return cls.from_dict(json.loads(json_str))

    def __repr__(self):
        return ", ".join(
            f"{movement.name.lower()}: {speed}"
            for movement, speed in self.speeds.items()
            if speed > 0
        ) or "no movement"


# ===== ABILITIES =====

class Abilities:
    def __init__(self, str_: int, dex_: int, con_: int,
                 int_: int, wis_: int, cha_: int):
        self.STR = str_
        self.DEX = dex_
        self.CON = con_
        self.INT = int_
        self.WIS = wis_
        self.CHA = cha_

    def to_dict(self):
        return {
            "STR": self.STR,
            "DEX": self.DEX,
            "CON": self.CON,
            "INT": self.INT,
            "WIS": self.WIS,
            "CHA": self.CHA,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            str_=data["STR"],
            dex_=data["DEX"],
            con_=data["CON"],
            int_=data["INT"],
            wis_=data["WIS"],
            cha_=data["CHA"],
        )

    def get_modifier(self, ability: str) -> int:
        value = getattr(self, ability.upper(), None)
        if value is None:
            raise ValueError(f"Unknown ability: {ability}")
        return (value - 10) // 2

    def __repr__(self):
        return ", ".join(f"{k}: {v}" for k, v in self.to_dict().items())


# ===== ACTION =====

@dataclass
class Action:
    name: str
    recharge: Optional[int] = None
    available: bool = True

    def recharge_roll(self):
        if self.recharge:
            self.available = random.randint(1, 6) >= self.recharge

    def to_dict(self):
        return {
            "name": self.name,
            "recharge": self.recharge,
            "available": self.available
        }

    @classmethod
    def from_dict(cls, data):
        action = cls(name=data["name"], recharge=data["recharge"])
        action.available = data.get("available", True)
        return action


# ===== STATBLOCK =====

@dataclass
class StatBlock:
    abilities: Abilities
    speed: Speed
    armor_class: int = 10
    max_HP: int = 1
    HP: int = None
    hit_dice: str = "1d8"
    proficiencies: dict = field(default_factory=dict)
    senses: dict = field(default_factory=dict)
    languages: List[str] = field(default_factory=list)
    traits: List[str] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    challenge_rating: str = "0"

    def __post_init__(self):
        if self.HP is None:
            self.HP = self.max_HP

    def take_damage(self, amount: int):
        self.HP = max(0, self.HP - amount)

    def heal(self, amount: int):
        self.HP = min(self.max_HP, self.HP + amount)

    def to_dict(self):
        return {
            "abilities": self.abilities.to_dict(),
            "speed": self.speed.to_dict(),
            "armor_class": self.armor_class,
            "max_HP": self.max_HP,
            "HP": self.HP,
            "hit_dice": self.hit_dice,
            "proficiencies": self.proficiencies,
            "senses": self.senses,
            "languages": self.languages,
            "traits": self.traits,
            "actions": [a.to_dict() for a in self.actions],
            "challenge_rating": self.challenge_rating,
        }

    @classmethod
    def from_dict(cls, data):
        abilities = Abilities.from_dict(data["abilities"])
        speed = Speed.from_dict(data["speed"])
        actions = [Action.from_dict(a) for a in data.get("actions", [])]
        return cls(
            abilities=abilities,
            speed=speed,
            armor_class=data.get("armor_class", 10),
            max_HP=data.get("max_HP", 1),
            HP=data.get("HP"),
            hit_dice=data.get("hit_dice", "1d8"),
            proficiencies=data.get("proficiencies", {}),
            senses=data.get("senses", {}),
            languages=data.get("languages", []),
            traits=data.get("traits", []),
            actions=actions,
            challenge_rating=data.get("challenge_rating", "0")
        )

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str):
        return cls.from_dict(json.loads(json_str))

    def __repr__(self):
        return (
            f"<StatBlock({self.abilities}; AC {self.armor_class}, "
            f"HP {self.HP}/{self.max_HP} ({self.hit_dice}), Speed [{self.speed}])>"
        )


# ===== COMBATANT =====

@dataclass
class Combatant:
    name: str
    statblock: StatBlock
    initiative: int
    is_pc: bool = False

    def take_damage(self, amount: int):
        self.statblock.take_damage(amount)

    def heal(self, amount: int):
        self.statblock.heal(amount)

    def recharge_actions(self):
        for action in self.statblock.actions:
            if not action.available and action.recharge:
                action.recharge_roll()

    def to_dict(self):
        return {
            "name": self.name,
            "statblock": self.statblock.to_dict(),
            "initiative": self.initiative,
            "is_pc": self.is_pc,
        }

    @classmethod
    def from_dict(cls, data):
        statblock = StatBlock.from_dict(data["statblock"])
        return cls(
            name=data["name"],
            statblock=statblock,
            initiative=data["initiative"],
            is_pc=data.get("is_pc", False),
        )
