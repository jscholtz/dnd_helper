import streamlit as st
import pandas as pd
from bestiary import StatBlock
import json
from collections import defaultdict

st.set_page_config(layout="wide")


@st.cache_data
def bestiary_data():
    with open("data/bestiary/bestiary-mm.json", "r") as f:
        data = json.load(f)

    statblocks = [StatBlock.from_json(item) for item in data["monster"][:500]]

    data_dict = defaultdict(list)

    df = pd.DataFrame()

    for item in statblocks:

        try:
            dictd = item.to_pandas_row()
        except Exception as e:
            print("================================")
            print(e)
            print(item)

        tdf = pd.DataFrame([dictd])
        df = pd.concat([df, tdf], ignore_index=True)

    return statblocks, df


all_data, df = bestiary_data()


def cr_edit(cr: str):
    cr = cr.split(" ")[0]
    if cr == "0":
        return 0.0
    elif cr == "1/8":
        return 0.125
    elif cr == "1/4":
        return 0.25
    elif cr == "1/2":
        return 0.5
    else:
        return float(cr)


df["cr_float"] = df["cr"].apply(cr_edit)

st.text_input("Search", key="search")
st.select_slider(
    "CR filter",
    options=[0, 0.125, 0.25, 0.5] + [i for i in range(1, 21)] + [25, 30],
    value=(0, 30),
    key="CR_limit",
)


mask = df["name"].apply(lambda x: x is not None)

if st.session_state.search:
    mask_t = df["name"].str.lower().str.contains(st.session_state.search.lower())
    mask = mask & mask_t
if st.session_state.CR_limit:
    st.write(f"{st.session_state.CR_limit}")
    mask_cr = df["cr_float"] >= st.session_state.CR_limit[0]
    mask_cr = mask_cr & (df["cr_float"] <= st.session_state.CR_limit[1])
    mask = mask & mask_cr

sel = st.dataframe(
    df[mask], hide_index=True, selection_mode="multi-row", on_select="rerun"
)

if sel:
    st.write(sel)
