import streamlit as st

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
        self.load_limit =self.load_break / (fact_safe * fact_important)
        
    
    def __repr__(self):
        return 'Cable object<Φ %s mm>' % self.diameter

#----------///Main///----------
#---/Title/---
st.title("RFR's Cable Calculator")

#---/Initiate the objects/---
material = Material("Cable", 1.6E5, 1.6E-5)
cable = None

#---/Define the cable/---
diam = st.selectbox("Select the diameter (mm):",
                    options = ["None", "30", "35", "45", "135"],
                    placeholder = "Select the target diameter...")
span = st.slider("Choose the span (m): ", 1, 100, 10, 1)

if diam != "None":
    cable = Cable(diam, span, material)
    [col_tri_1, col_tri_2, col_tri_3] = st.columns(3)
    col_tri_1.metric("Section area: ", str(cable.area) + " mm2")
    col_tri_2.metric("Limit tension: ", str(int(cable.load_limit)) + " kN")
    col_tri_3.metric("Breaking load: ", str(cable.load_break) + " kN")
