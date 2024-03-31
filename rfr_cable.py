import scipy as sp
import pandas as pd

#----------///Class definitions///----------
class Material:
    def __init__(self, txt_name, num_E, num_therm):
        self.name = txt_name
        self.type = 'Cable'
        self.E = num_E #Young's modulus of cable in MPa (N/mm2)
        self.therm = num_therm #Thermal expansion rate of cable in 1/°C

class Cable:
    def __init__(self):
        #---//General information//---
        self.area = None
        self.load_break = None
        self.load_limit = None
    
    def update(self, dict_diam, txt_diam, num_span, obj_material):
        #---//General information//---
        self.span = num_span
        self.material = obj_material
        
        #---//Get the cable limit load//---
        try:
            self.area = dict_diam[txt_diam][0] #Area in mm2
            self.load_break = dict_diam[txt_diam][1] #Breaking load in kN
        except:
            raise Exception('The input diameter is not in table!')
        self.diameter = float(txt_diam) #Diameter in mm
        fact_safe = 1.5
        fact_important = 1.0
        self.load_limit = round(self.load_break / (fact_safe * fact_important), 1)
    
    def is_valid(self):
        if self.area == None:
            return False
        else:
            return True
        

#----------///Method definition///----------
def read_cable_table(path):
    table = pd.read_csv(path)
    Headers = table.columns
    Diams = []
    dict = {}
    for row in table.iterrows():
        content = row[1]
        diam = str(int(content[Headers[0]]))
        Diams.append(diam)
        area = content[Headers[1]]
        load_break = content[Headers[2]]
        load_limit = content[Headers[3]]
        dict[diam] = (area, load_break, load_limit)
    return table, Diams, dict

def calc_cable(cable, load, prestress, temperature, lim):
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
    
    #---//Get the limitation of force//---
    lim_tension = cable.load_limit
    utility = round(force / lim_tension, 2)
    
    #---//Get the deflection//---
    deflect = q * l**2 / 8 / force * 1000 #Transfer from m to mm
    lim_deflect = lim * l * 1000 #Transfer from m to mm

    return force, utility, deflect, lim_deflect