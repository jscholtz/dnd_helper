from dataclasses import dataclass, field
from typing import List, Union, Optional, Dict, Any


# --- Damage Types with Notes ---


@dataclass
class DamageModifierNote:
    types: List[str]
    note: str


@dataclass
class DamageModifier:
    entries: List[Union[str, DamageModifierNote]] = field(default_factory=list)


# --- Speed and Movement ---


@dataclass
class SpeedEntry:
    number: int
    condition: Optional[str] = None


@dataclass
class Speed:
    modes: Dict[str, Union[int, SpeedEntry]] = field(default_factory=dict)


# --- Abilities ---


@dataclass
class AbilityScores:
    str_: int
    dex_: int
    con_: int
    int_: int
    wis_: int
    cha_: int


# --- Actions / Traits / Legendary ---


@dataclass
class NestedEntry:
    type_: str
    style: Optional[str] = None
    items: List[Union[str, Dict[str, str]]] = field(default_factory=list)


@dataclass
class Action:
    name: str
    entries: List[Union[str, NestedEntry]]


@dataclass
class SpellSlot:
    level: int
    slots: Optional[int] = None
    spells: List[str] = field(default_factory=list)


@dataclass
class Spellcasting:
    name: str
    headerEntries: List[str] = field(default_factory=list)
    spells: Dict[int, SpellSlot] = field(default_factory=dict)
    footerEntries: Optional[List[str]] = None


@dataclass
class CreatureType:
    type_: str
    tags: Optional[List[str]] = None


# --- Main StatBlock ---


@dataclass
class StatBlock:
    name: str
    size: str
    type_: Union[str, CreatureType]
    source: str
    alignment: Union[str, List[str]]

    ac: Union[int, str]
    hp: Dict[str, Union[int, str]]  # { average: 90, formula: "12d10+24" }

    speed: Speed

    abilities: AbilityScores

    saves: Optional[Dict[str, str]] = None
    skills: Optional[Dict[str, str]] = None

    resist: DamageModifier = field(default_factory=DamageModifier)
    immune: DamageModifier = field(default_factory=DamageModifier)
    vulnerable: DamageModifier = field(default_factory=DamageModifier)

    conditionImmune: List[str] = field(default_factory=list)

    senses: Optional[str] = None
    passive: Optional[int] = None
    languages: Union[str, List[str], None] = None
    cr: Union[int, str, None] = None

    trait: List[Action] = field(default_factory=list)
    action: List[Action] = field(default_factory=list)
    legendary: Optional[List[Action]] = None

    page: Optional[int] = None
    spellcasting: Optional[List[Spellcasting]] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "StatBlock":
        # Parse basic fields
        name = data["name"]
        size = data["size"]
        type_ = data["type"]
        if isinstance(type_, dict):
            type_ = CreatureType(type_=type_["type"], tags=type_.get("tags"))
        source = data["source"]
        alignment = data["alignment"]

        if isinstance(alignment, str):
            alignment = [alignment]
        if isinstance(alignment, list):
            if len(alignment) > 0:
                if isinstance(alignment[0], dict):
                    temp = []
                    for al in alignment:
                        datat = dict(al)
                        temp.append(
                            ",".join(datat["alignment"]) + f" {datat['chance']}%"
                        )
                    alignment = temp

        ac = data["ac"]
        hp = data["hp"]
        speed = Speed(
            modes={
                key: (SpeedEntry(number=value) if isinstance(value, dict) else value)
                for key, value in data["speed"].items()
            }
        )
        abilities = AbilityScores(
            str_=data["str"],
            dex_=data["dex"],
            con_=data["con"],
            int_=data["int"],
            wis_=data["wis"],
            cha_=data["cha"],
        )

        saves = data.get("save")
        skills = data.get("skill")

        # Parse resistances, immunities, and vulnerabilities
        def parse_damage_modifiers(modifiers: Any, key) -> DamageModifier:
            damage_modifier = DamageModifier()
            if isinstance(modifiers, list):
                for modifier in modifiers:
                    if isinstance(modifier, str):
                        damage_modifier.entries.append(modifier)
                    else:
                        if key in modifier:
                            damage_modifier.entries.append(
                                DamageModifierNote(
                                    types=modifier[key], note=modifier.get("note", "")
                                )
                            )
                        else:
                            damage_modifier.entries.append(modifier)
            return damage_modifier

        resist = parse_damage_modifiers(data.get("resist", []), "resist")
        immune = parse_damage_modifiers(data.get("immune", []), "immune")
        vulnerable = parse_damage_modifiers(data.get("vulnerable", []), "vulnerable")

        # Parse condition immunities
        conditionImmune = data.get("conditionImmune", [])

        # Parse senses, passive, languages, CR
        senses = data.get("senses")
        passive = data.get("passive")
        languages = data.get("languages")
        cr = data.get("cr")

        # Parse traits, actions, legendary actions
        def parse_actions(actions: List[Dict[str, Any]]) -> List[Action]:
            parsed_actions = []
            for action in actions:
                entries = []
                for entry in action["entries"]:
                    if isinstance(entry, dict):
                        entries.append(
                            NestedEntry(
                                type_=entry["type"],
                                style=entry.get("style"),
                                items=entry["items"],
                            )
                        )
                    else:
                        entries.append(entry)
                parsed_actions.append(Action(name=action["name"], entries=entries))
            return parsed_actions

        trait = parse_actions(data.get("trait", []))
        action = parse_actions(data.get("action", []))
        legendary = (
            parse_actions(data.get("legendary", [])) if "legendary" in data else None
        )

        # Parse page
        page = data.get("page")

        def parse_spellcasting(sc_data: Any) -> List[Spellcasting]:
            result: List[Spellcasting] = []
            for block in sc_data:
                slots_map: Dict[int, SpellSlot] = {}
                for lvl_str, info in block.get("spells", {}).items():
                    lvl = int(lvl_str)
                    slots = info.get("slots")
                    spells = info.get("spells", [])
                    slots_map[lvl] = SpellSlot(level=lvl, slots=slots, spells=spells)
                result.append(
                    Spellcasting(
                        name=block["name"],
                        headerEntries=block.get("headerEntries", []),
                        spells=slots_map,
                        footerEntries=block.get("footerEntries"),
                    )
                )
            return result

        spellcasting = parse_spellcasting(data.get("spellcasting", []))

        # Create and return the StatBlock object
        return cls(
            name=name,
            size=size,
            type_=type_,
            source=source,
            alignment=alignment,
            ac=ac,
            hp=hp,
            speed=speed,
            abilities=abilities,
            saves=saves,
            skills=skills,
            resist=resist,
            immune=immune,
            vulnerable=vulnerable,
            conditionImmune=conditionImmune,
            senses=senses,
            passive=passive,
            languages=languages,
            cr=cr,
            trait=trait,
            action=action,
            legendary=legendary,
            page=page,
            spellcasting=spellcasting,
        )

    def to_pandas_row(self):
        # Flatten basic attributes
        row = {
            "name": self.name,
            "size": self.size,
            "type": (
                self.type_.type_ if isinstance(self.type_, CreatureType) else self.type_
            ),
            "source": self.source,
            "alignment": (
                ", ".join(self.alignment)
                if isinstance(self.alignment, list)
                else self.alignment
            ),
            "ac": self.ac,
            "hp_avg": self.hp.get("average"),
            "hp_formula": self.hp.get("formula"),
            "passive": self.passive,
            "languages": (
                ", ".join(self.languages)
                if isinstance(self.languages, list)
                else self.languages
            ),
            "page": self.page,
            "senses": self.senses,
        }

        if self.cr is not None:
            if isinstance(self.cr, int):
                row["cr"] = str(self.cr)
            elif isinstance(self.cr, str):
                row["cr"] = self.cr
            elif isinstance(self.cr, float):
                row["cr"] = f"{self.cr:.2f}"
            elif isinstance(self.cr, dict):
                if "lair" in self.cr:
                    row["cr"] = f"{self.cr["cr"]} (lair {self.cr['lair']})"
                if "coven" in self.cr:
                    row["cr"] = f"{self.cr["cr"]} (coven {self.cr['coven']})"

        # Flatten Speed (modes as comma-separated list or number)
        for mode, value in self.speed.modes.items():
            if isinstance(value, SpeedEntry):
                row[f"speed_{mode}"] = (
                    f"{value.number} ({value.condition})"
                    if value.condition
                    else str(value.number)
                )
            else:
                row[f"speed_{mode}"] = str(value)

        # Flatten Abilities (Ability Scores)
        for ability, score in self.abilities.__dict__.items():
            row[ability] = score

        # Flatten Damage Modifiers (Resist, Immune, Vulnerable)
        def flatten_damage_modifier(modifier: DamageModifier, prefix: str):
            entries = []
            for entry in modifier.entries:
                if isinstance(entry, DamageModifierNote):
                    entries.append(f"{', '.join(entry.types)} (Note: {entry.note})")
                else:
                    entries.append(str(entry))
            row[f"{prefix}"] = ", ".join(entries)

        flatten_damage_modifier(self.resist, "resist")
        flatten_damage_modifier(self.immune, "immune")
        flatten_damage_modifier(self.vulnerable, "vulnerable")

        # Flatten condition immunities as a comma-separated list
        row["conditionImmune"] = ", ".join(self.conditionImmune)

        # Flatten Traits and Actions (as list of string representations)
        def flatten_actions(actions: List[Action], prefix: str):
            action_strings = []
            for action in actions:
                action_str = f"{action.name}: "
                entries = []
                for entry in action.entries:
                    if isinstance(entry, NestedEntry):
                        entries.append(
                            f"{entry.type_} ({', '.join(str(item) for item in entry.items)})"
                        )
                    else:
                        entries.append(str(entry))
                action_strings.append(action_str + "; ".join(entries))
            row[f"{prefix}"] = "; ".join(action_strings)

        flatten_actions(self.trait, "trait")
        flatten_actions(self.action, "action")

        if self.legendary:
            flatten_actions(self.legendary, "legendary")

        # Spellcasting (currently ignored, you can follow the same pattern if needed)

        return row
