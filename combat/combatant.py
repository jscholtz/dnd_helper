from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import json
import random


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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

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
    entries: List[str] = field(default_factory=list)
    recharge: Optional[int] = None
    available: bool = True

    def recharge_roll(self):
        if self.recharge:
            self.available = random.randint(1, 6) >= self.recharge

    def to_dict(self):
        return {
            "name": self.name,
            "entries": self.entries,
            "recharge": self.recharge,
            "available": self.available
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            entries=data.get("entries", []),
            recharge=data.get("recharge"),
            available=data.get("available", True)
        )


# ===== STATBLOCK =====

@dataclass
class StatBlock:
    name: str
    size: str = "Medium"
    creature_type: str = ""
    alignment: List[str] = ""
    source: str = "MM"
    armor_class: int = 10
    armor_desc: Optional[str] = None
    hit_dice: str = "1d8"
    max_HP: int = 1
    speed: Speed = field(default_factory=Speed)
    abilities: Abilities = field(default_factory=lambda: Abilities(10, 10, 10, 10, 10, 10))
    saves: Dict[str, str] = field(default_factory=dict)
    skills: Dict[str, str] = field(default_factory=dict)
    senses: str = ""
    passive_perception: int = 10
    languages: str = ""
    challenge_rating: str = "0"
    traits: List[Action] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    legendary: List[Action] = field(default_factory=list)
    legendary_group: Optional[str] = None
    page: Optional[int] = None

    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "type": self.creature_type,
            "alignment": self.alignment,
            "source": self.source,
            "armor_class": self.armor_class,
            "armor_desc": self.armor_desc,
            "hit_dice": self.hit_dice,
            "max_HP": self.max_HP,
            "speed": self.speed.to_dict(),
            "abilities": self.abilities.to_dict(),
            "saves": self.saves,
            "skills": self.skills,
            "senses": self.senses,
            "passive_perception": self.passive_perception,
            "languages": self.languages,
            "challenge_rating": self.challenge_rating,
            "traits": [a.to_dict() for a in self.traits],
            "actions": [a.to_dict() for a in self.actions],
            "legendary": [a.to_dict() for a in self.legendary],
            "legendary_group": self.legendary_group,
            "page": self.page
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            size=data["size"],
            creature_type=data["type"],
            alignment=data.get("alignment", []),
            source=data.get("source", ""),
            armor_class=int(data["ac"].split()[0]) if isinstance(data["ac"], str) else data["ac"],
            armor_desc=" ".join(data["ac"].split()[1:]) if isinstance(data["ac"], str) and " " in data["ac"] else None,
            hit_dice=data["hp"]["formula"],
            max_HP=data["hp"]["average"],
            speed=Speed.from_dict(data.get("speed", {})),
            abilities=Abilities(
                str_=data["str"], dex_=data["dex"], con_=data["con"],
                int_=data["int"], wis_=data["wis"], cha_=data["cha"]
            ),
            saves=data.get("save", {}),
            skills=data.get("skill", {}),
            senses=data.get("senses", ""),
            passive_perception=data.get("passive", 10),
            languages=data.get("languages", ""),
            challenge_rating=data.get("cr", "0"),
            traits=[Action(name=t["name"], entries=t.get("entries", [])) for t in data.get("trait", [])],
            actions=[Action(name=a["name"], entries=a.get("entries", [])) for a in data.get("action", [])],
            legendary=[Action(name=l["name"], entries=l.get("entries", [])) for l in data.get("legendary", [])],
            legendary_group=data.get("legendaryGroup"),
            page=data.get("page")
        )


# ===== COMBATANT =====

@dataclass
class Combatant:
    name: str
    statblock: StatBlock
    initiative: int
    HP: Optional[int] = None
    is_pc: bool = False

    def __post_init__(self):
        if self.HP is None:
            self.HP = self.statblock.max_HP

    def take_damage(self, amount: int):
        self.HP = max(0, self.HP - amount)

    def heal(self, amount: int):
        self.current_HP = min(self.statblock.max_HP, self.HP + amount)

    def recharge_actions(self):
        for action in self.statblock.actions + self.statblock.legendary:
            if not action.available and action.recharge:
                action.recharge_roll()

    def to_dict(self):
        return {
            "name": self.name,
            "initiative": self.initiative,
            "current_HP": self.current_HP,
            "is_pc": self.is_pc,
            "statblock": self.statblock.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            initiative=data["initiative"],
            current_HP=data.get("current_HP"),
            is_pc=data.get("is_pc", False),
            statblock=StatBlock.from_dict(data["statblock"])
        )
