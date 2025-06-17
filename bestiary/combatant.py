import uuid
from typing import Optional

class Combatant:
    def __init__(self, name: str, statblock: StatBlock, current_hp: Optional[int] = None, id_: Optional[str] = None):
        self.name = name
        self.statblock = statblock
        self.id = id_ or str(uuid.uuid4())
        # Initialize current HP with the "average" value from the statblock's hp dictionary, or 0 if not defined.
        self.current_hp = current_hp if current_hp is not None else statblock.hp.get("average", 0)
        # Initiative will be set later during combat.
        self.initiative: Optional[int] = None

    def take_damage(self, damage: int) -> None:
        """
        Applies damage to the combatant, reducing current_hp. It does not allow current_hp to drop below zero.
        """
        self.current_hp = max(self.current_hp - damage, 0)

    def heal(self, amount: int) -> None:
        """
        Heals the combatant, but current_hp won't exceed the statblock's average (assumed max HP).
        """
        max_hp = self.statblock.hp.get("average", 0)
        self.current_hp = min(self.current_hp + amount, max_hp)

    def set_initiative(self, initiative: int) -> None:
        """
        Sets the combatant's initiative value.
        """
        self.initiative = initiative

    def update_hp(self, new_hp: int) -> None:
        """
        Directly update the combatant's current hit points.
        """
        self.current_hp = max(new_hp, 0)  # avoid negative HP

    def __repr__(self):
        return (f"<Combatant {self.name} (HP: {self.current_hp}, Initiative: {self.initiative}, "
                f"ID: {self.id})>")
