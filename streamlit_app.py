import streamlit as st
from rfr_cable import *

#----------///Method definition///----------
def float_input(txt, is_possitive):
    [col1, col2] = st.columns(2)
    num = 0
    txt_input = col1.text_input(txt, value = "")
    if txt_input != "":
        try:
            num = float(txt_input)
            if is_possitive and num <= 0:
                col2.write("")
                col2.warning("Must be possitive!", icon = "⚠️")
                num = 0
        except:
            col2.write("")
            col2.warning("Enter numbers only!", icon = "⚠️")
    return num

def eval_input(txt, is_possitive):
    [col1, col2] = st.columns(2)
    num = 1/65
    txt_input = col1.text_input(txt, value = "1/65")
    if txt_input != "1/65":
        try:
            num = eval(txt_input)
            if is_possitive and num <= 0:
                col2.write("")
                col2.warning("Must be possitive!", icon = "⚠️")
                num = 1/65
        except:
            col2.write("")
            col2.warning("Invalid input!", icon = "⚠️")
    return num

#----------///Main///----------
#---/Title/---
st.title("RFR's Cable Calculator")

#---/Initiate the objects/---
material = Material("Cable", 1.6E5, 1.6E-5)
cable = Cable()
dict_cable = {}
load = None
prestress = None

#---/Define the cable/---
st.markdown("---")
st.header("Cable Definition: ")
[col_bi_1, col_bi_2] = st.columns(2) #Location in code matters
type_cable = col_bi_1.selectbox("Select the cable type:",
                          options = ["Spiral Strand (SS)", "Full Locked Cable (FLC)"])
[table_cable, Lst_diam, dict_cable] = read_cable_table("Data//" + type_cable + ".CSV")
view_table = col_bi_1.checkbox("Read all cable properties", False)
if view_table:
    st.dataframe(table_cable, hide_index = True)
Lst_diam.insert(0, "None")
diam = col_bi_2.selectbox("Select the diameter (mm):",
                          options = Lst_diam)
span = float_input("Enter the span l (m): ", True)
if dict_cable and diam != "None":
    cable.update(dict_cable, diam, span, material)
[col_tri_1, col_tri_2, col_tri_3] = st.columns(3) #Location in code matters
col_tri_1.metric("Section area A: ", str(cable.area) + " mm²")
col_tri_2.metric("Limit tension: ", str(cable.load_limit) + " kN")
col_tri_3.metric("Breaking load: ", str(cable.load_break) + " kN")

#---/Define the loads/---
st.markdown("---")
st.header("Load Definition: ")
load = float_input("Enter the load q (kN/m): ", True)
temperature = float_input("Enter the temperature change ΔT (°C): ", False)

#---/Calculation/---
#-/Input/-
st.markdown("---")
st.header("Calculation: ")
st.latex(r"H^{2} (H - V) + H^{2} EA(\alpha_{t} \cdot \Delta T)=\frac{E A \cdot q^{2} l^{2}}{24}")
prestress_ini = float_input("Guess a presstress force V (kN): ", True)
if prestress_ini:
    prestress_ini = int(prestress_ini)
    prestress_min = int(prestress_ini - 200)
    prestress_max = int(prestress_ini + 200)
    if prestress_min < 0:
        prestress_min = 0
    prestress = st.slider("You can also vary the presstress a bit...",
                          prestress_min, prestress_max, prestress_ini, 1)
lim = eval_input("Enter the limit deflection ratio: ", True)

#-/Output/-
if cable and load and temperature and prestress and lim:
    [force, utility, deflect, deflect_lim] = calc_cable(cable,
                            load, prestress, temperature, lim)
    
    #-/Force/-
    [col_tri_1, col_tri_2, col_tri_3] = st.columns(3) #Location in code matters
    force_delta = round(cable.load_limit - force, 2)
    col_tri_1.metric("The force at support H: ", "{0} kN".format(round(force, 2)))
    col_tri_2.metric("Limit tension: ", str(cable.load_limit) + " kN",
                     str(force_delta) + " kN")
    if utility < 1:
        col_tri_3.write("")
        col_tri_3.success("Utility: {0} OK!".format(utility))
    else:
        col_tri_3.write("")
        col_tri_3.error("Utility: {0} Fail!".format(utility))
    
    #-/Deflection/-
    [col_tri_1, col_tri_2, col_tri_3] = st.columns(3) #Location in code matters
    deflect_delta = round(deflect_lim - deflect, 2)
    col_tri_1.metric("Deflection at mid-span: ", "{0} mm".format(round(deflect, 2)))
    col_tri_2.metric("Limit deflection: ", "{0} mm".format(round(deflect_lim, 2)),
                     str(deflect_delta) + " mm")
    if deflect < deflect_lim:
        col_tri_3.write("")
        col_tri_3.success("OK!")
    else:
        col_tri_3.write("")
        col_tri_3.error("Fail!")
