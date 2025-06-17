import streamlit as st
from combat import Combatant, Action, Encounter, default_encounter
from math import ceil
import json

st.set_page_config(layout="wide")

# === Trigger rerun flag ===

if "rerun" not in st.session_state:
    st.session_state.rerun = False
elif st.session_state.rerun:
    st.session_state.rerun = False
    st.toast("Rerunning...")
    st.rerun()


# === Decorated dialogs ===

@st.dialog("💾 Save Battle")
def show_save_dialog():
    if "battle" in st.session_state and st.session_state.battle is not None:
        battle_json = json.dumps(st.session_state.battle.to_dict(), indent=2)
        st.download_button(
            label="📥 Download Battle JSON",
            data=battle_json.encode("utf-8"),
            file_name="battle.json",
            mime="application/json"
        )
    else:
        st.warning("No battle is currently loaded to save.")


@st.dialog("📂 Load Battle")
def show_load_dialog():
    uploaded_file = st.file_uploader("Upload a battle JSON file", type=["json"])
    if uploaded_file:
        try:
            contents = uploaded_file.read()
            data = json.loads(contents)
            st.session_state.battle = Encounter.from_dict(data)
            st.success("✅ Battle loaded successfully!")
            st.session_state.rerun = True  # Trigger a rerun to refresh the UI with the new data
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error loading battle: {e}")


# --- Session Setup ---
if 'battle' not in st.session_state:
    # Example data
    combatants = default_encounter
    st.session_state.battle = Encounter(combatants)

if "selected_combatant" not in st.session_state:
    st.session_state.selected_combatant = None

battle: Encounter = st.session_state.battle
current = battle.get_current()

# --- Page Title ---
#st.title(f"Encounter, round {battle.round} ")

st.markdown(
    """
    <style>
        .stProgress > div > div > div > div {
            background-color: green;
        }

        /* Style for the empty part of the progress bar */
        .stProgress > div > div > div {
            background-color: red;
        }
    </style>""",
    unsafe_allow_html=True,
)


def render_combatant_card(combatant, is_current=False):
    # # Create button that acts like a card

    with st.container(border=True):
        if is_current:
            text = f":blue[{combatant.name}]"
        else:
            text = f"{combatant.name}"


        cols = st.columns([1,4], vertical_alignment="center")
        with cols[0]:
            if st.button("🎯", key=f"card_{combatant.name}"):
                st.session_state.selected_combatant = combatant.name
        with cols[1]:
            st.subheader(f"{text}")

        st.write(f"**Initiative:** {combatant.initiative}")

        if combatant.is_pc:

            st.markdown("\n\n.\n\n.\n\n")
            return

        st.progress(combatant.HP / combatant.statblock.max_HP)
        #with st.container(border=True):
        fmt_cols_5 = [1.5,2,0.25,1.5,2]

        cols = st.columns(fmt_cols_5)
        cols[0].write("HP")
        cols[1].write(f"{combatant.HP}/{combatant.statblock.max_HP}")
        cols[3].write("AC")
        cols[4].write(f"{combatant.statblock.armor_class}")

        cols = st.columns(fmt_cols_5)
        cols[0].write("STR")
        cols[3].write("INT")
        cols[1].write(f"{combatant.statblock.abilities.STR} ({combatant.statblock.abilities.get_modifier('STR')})")
        cols[4].write(f"{combatant.statblock.abilities.INT} ({combatant.statblock.abilities.get_modifier('INT')})")

        cols = st.columns(fmt_cols_5)
        cols[0].write("CON")
        cols[1].write(f"{combatant.statblock.abilities.CON} ({combatant.statblock.abilities.get_modifier('CON')})")
        cols[3].write("WIS")
        cols[4].write(f"{combatant.statblock.abilities.WIS} ({combatant.statblock.abilities.get_modifier('WIS')})")

        cols = st.columns(fmt_cols_5)
        cols[0].write("DEX")
        cols[3].write("CHA")
        cols[1].write(f"{combatant.statblock.abilities.DEX} ({combatant.statblock.abilities.get_modifier('DEX')})")
        cols[4].write(f"{combatant.statblock.abilities.CHA} ({combatant.statblock.abilities.get_modifier('CHA')})")

        st.write(str(combatant.statblock.speed))
        if combatant.statblock.senses:
            print(combatant.statblock.senses)
        if combatant.statblock.saves:
            print(combatant.statblock.saves)

        if combatant.statblock.traits:
            print(combatant.statblock.traits)
        if combatant.statblock.languages:
            print(combatant.statblock.languages)


        for action in combatant.statblock.actions:
            cols = st.columns([1,4], vertical_alignment="center")
            with cols[0]:
                if action.available:
                    if st.button(f"🔥",
                                 key=f"action_{combatant.name}_{action.name}",
                                 disabled=not (action.available and is_current),
                                 use_container_width=True):
                        if action.recharge:
                            action.available = False  # Only mark unavailable if it's rechargeable
                        st.rerun()
                else:
                    st.button(f"❌",
                              disabled=True,
                              key=f"action_{combatant.name}_{action.name}",
                              use_container_width=True)
            with cols[1]:
                st.write(f"{action.name}")

# --- Render All Combatants as Cards ---
cards_per_row = 6
num_rows = ceil(len(battle.combatants) / cards_per_row)


for row in range(num_rows):
    cols = st.columns(cards_per_row)
    for i in range(cards_per_row):
        index = row * cards_per_row + i
        if index < len(battle.combatants):
            combatant = battle.combatants[index]
            with cols[i]:
                render_combatant_card(combatant, is_current=(index == battle.turn_index))

with st.sidebar:
    st.subheader(f"Round {battle.round}")

    if st.button("💾 Save Battle", use_container_width=True,):
        show_save_dialog()

    if st.button("📂 Load Battle", use_container_width=True,):
        show_load_dialog()

    if st.button("➡️ Next Turn", use_container_width=True, type="primary"):
        battle.next_turn()
        st.rerun()

    if st.session_state.selected_combatant:

        combatant_names = [c.name for c in battle.combatants]
        selected_name = st.session_state.selected_combatant
        selected_combatant = next((c for c in battle.combatants if c.name == selected_name), None)

        if selected_combatant:
            with st.container(border=True):
                st.subheader(f"{st.session_state.selected_combatant}")
                st.text(f"Hit Points: {selected_combatant.statblock.HP}/{selected_combatant.statblock.max_HP}")
                st.text(f"Initiative: {selected_combatant.initiative}")
            with st.form(f"adjust_hp_form_{selected_name}"):
                hp_delta = st.number_input("Damage (positive) or healing (negative)", value=0)
                if st.form_submit_button("Apply Change"):
                    if hp_delta >= 0:
                        selected_combatant.take_damage(hp_delta)
                    else:
                        selected_combatant.heal(-hp_delta)
                    st.rerun()  # Force refresh so the cards update
