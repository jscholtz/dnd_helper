from .combatant import Combatant, Action, StatBlock, Abilities, Speed

default_encounter = [
    Combatant(
        name="Hero 1",
        is_pc=True,
        initiative=18,
        HP=35,
        statblock=StatBlock(
            name="PC",
            abilities=Abilities(str_=16, dex_=14, con_=14, int_=10, wis_=12, cha_=10),
            max_HP=35,
            speed=Speed(walk=30),
            hit_dice="5d10",
            actions=[
                Action("**Cleave** (+7, 1d10+7)", recharge=6),
                Action("**Shield Bash**")
            ]
        ),

    ),
    Combatant(
        name="Goblin A",
        initiative=15,
        HP=12,
        statblock=StatBlock(
            name="Goblin",
            abilities=Abilities(str_=8, dex_=14, con_=10, int_=8, wis_=8, cha_=8),
            speed=Speed(walk=30),
            hit_dice="2d6",
            actions=[Action("**Slash** (+3, 1d6+3)")],
            max_HP=14,

        ),
    ),

    Combatant(
        name="Goblin King",
        initiative=10,
        HP=20,
        statblock=StatBlock(
            name="Goblin King",
            abilities=Abilities(str_=14, dex_=12, con_=12, int_=10, wis_=10, cha_=10),
            max_HP=22,
            speed=Speed(walk=30),
            hit_dice="4d8",
            actions=[
                Action("**Javelin** (+4, 1d8+6)"),
                Action("**Fart** [poison]  CON 16, 3d4+3", recharge=2)]
        )
    )
]
