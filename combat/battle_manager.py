import json
from .combatant import Combatant


class Encounter:
    def __init__(self, combatants: list[Combatant]):
        self.round = 1
        self.combatants = sorted(combatants, key=lambda x: x.initiative, reverse=True)
        self.turn_index = 0

    def next_turn(self):
        """Advance to the next combatant's turn, recharging actions if needed."""
        self.turn_index = (self.turn_index + 1) % len(self.combatants)

        # Recharge actions at start of each turn
        self.combatants[self.turn_index].recharge_actions()

        # Increment round if back to first combatant
        if self.turn_index == 0:
            self.round += 1

    def get_current(self) -> Combatant:
        """Return the combatant whose turn it currently is."""
        return self.combatants[self.turn_index]

    def get_previous(self) -> list[Combatant]:
        """Combatants who have already acted this round."""
        return self.combatants[:self.turn_index]

    def get_upcoming(self) -> list[Combatant]:
        """Combatants who are still to act this round."""
        return self.combatants[self.turn_index + 1:]

    def to_dict(self) -> dict:
        return {
            "round": self.round,
            "turn_index": self.turn_index,
            "combatants": [c.to_dict() for c in self.combatants]
        }

    @classmethod
    def from_dict(cls, data: dict):
        combatants = [Combatant.from_dict(c) for c in data["combatants"]]
        instance = cls(combatants)
        instance.round = data["round"]
        instance.turn_index = data["turn_index"]
        return instance

    def save(self, filepath: str):
        """Save current battle state to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, filepath: str):
        """Load battle state from a JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
