import streamlit as st
import scipy as sp

#----------///Class definitions///----------
class Material:
    def __init__(self, txt_name, num_E, num_therm):
        self.name = txt_name
        self.type = 'Cable'
        self.E = num_E #Young's modulus of cable in MPa (N/mm2)
        self.therm = num_therm #Thermal expansion rate of cable in 1/°C
    
    def __repr__(self):
        return 'Material object<%s>' % self.name

class Cable:
    def __init__(self, txt_diam, num_span, obj_material):
        #---//General information//---
        self.span = num_span
        self.material = obj_material
        
        #---//Get the cable limit load//---
        dict_diam = {'25': {'area': 440, 'load': 596},
                     '30': {'area': 648, 'load': 858},
                     '35': {'area': 842, 'load': 1170},
                     '45': {'area': 1180, 'load': 1830},
                     '135': {'area': 12368, 'load': 17400}}
        try:
            self.area = dict_diam[txt_diam]['area'] #Area in mm2
            self.load_break = dict_diam[txt_diam]['load'] #Breaking load in kN
        except:
            raise Exception('The input diameter is not in table!')
        self.diameter = float(txt_diam) #Diameter in mm
        fact_safe = 1.5
        fact_important = 1.0
        self.load_limit = int(self.load_break / (fact_safe * fact_important))
        
    
    def __repr__(self):
        return 'Cable object<Φ %s mm>' % self.diameter

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

def calc_cable(cable, load, prestress, temperature):
    #---/Define private methods/---
    def _func_origin(H):
        """The original function"""
        asb1 = H**2 * (H - V)
        asb2 = E * A * H**2 * at * T
        asb3 = E * A * q**2 * l**2 / 24
        result = asb1 + asb2 - asb3
        return result

    def _func_deriv(H):
        """The 1st derivative of the original function"""
        asb1 = H * (3 * H - 2 * V)
        asb2 = E * A * 2 * H * at * T
        result = asb1 + asb2
        return result

    #---/Define global constants/---
    #-/General data/-
    V = prestress #Prestress tension load in kN
    q = load #Applied design load in kN/m
    T = temperature #The temperature change in °C

    #-/Extract data from the cable object/-
    E = cable.material.E * 1000 #Young's modulus in KPa(kN/m2)
    A = cable.area / 1000000 #Area of cable in m2
    at = cable.material.therm #Thermal expansion rate in 1/°C
    l = cable.span #The span of cable in m

    #---//Find the root//---
    force = sp.optimize.newton(func = _func_origin, x0 = V, fprime = _func_deriv,
                            tol = 1E-4, maxiter = 100) #Support force in kN

    #---//Get the limitation of deflection//---
    lim_tension = cable.load_limit
    utility = round(force / lim_tension, 2)

    return force, utility

#----------///Main///----------
#---/General settings/---
[col_tri_1, col_tri_2, col_tri_3] = st.columns(3)

#---/Title/---
st.title("RFR's Cable Calculator")

#---/Initiate the objects/---
material = Material("Cable", 1.6E5, 1.6E-5)
cable = None
load = None
prestress = None

#---/Define the cable/---
st.markdown("---")
st.header("Cable Definition: ")
diam = st.selectbox("Select the diameter (mm):",
                    options = ["None", "30", "35", "45", "135"],
                    placeholder = "Select the target diameter...")
span = float_input("Enter the span (m): ", True)
[col_tri_1, col_tri_2, col_tri_3] = st.columns(3) #Location in code matters
if diam == "None":
    col_tri_1.metric("Section area: ", "None")
    col_tri_2.metric("Limit tension: ", "None")
    col_tri_3.metric("Breaking load: ", "None")
else:
    cable = Cable(diam, span, material)
    col_tri_1.metric("Section area: ", str(cable.area) + " mm²")
    col_tri_2.metric("Limit tension: ", str(cable.load_limit) + " kN")
    col_tri_3.metric("Breaking load: ", str(cable.load_break) + " kN")

#---/Define the loads/---
st.markdown("---")
st.header("Load Definition: ")
load = float_input("Enter the load (kN/m): ", True)
temperature = float_input("Enter the delta temperature (°C): ", False)

#---/Calculation/---
st.markdown("---")
st.header("Calculation: ")
prestress_ini = float_input("Guess a presstress force (kN): ", True)
if prestress_ini:
    prestress_ini = int(prestress_ini)
    prestress_min = int(prestress_ini - 200)
    prestress_max = int(prestress_ini + 200)
    if prestress_min < 0:
        prestress_min = 0
    print(prestress_ini, prestress_min, prestress_max)
    prestress = st.slider("You can also vary the presstress a bit...",
                          prestress_min, prestress_max, prestress_ini, 1)
[col_tri_1, col_tri_2, col_tri_3] = st.columns(3) #Location in code matters
if cable and load and temperature and prestress:
    [force, utility] = calc_cable(cable, load, prestress, temperature)
    force_delta = round(cable.load_limit - force, 2)
    col_tri_1.metric("The force at support: ", "{0} kN".format(round(force, 2)))
    col_tri_2.metric("Limit tension: ", str(cable.load_limit) + " kN",
                     str(force_delta) + " kN")
    if utility < 1:
        col_tri_3.write("")
        col_tri_3.success("Utility: {0} OK!".format(utility))
    else:
        col_tri_3.write("")
        col_tri_3.error("Utility: {0} Fail!".format(utility))
