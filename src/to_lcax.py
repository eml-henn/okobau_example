import mysql.connector
import epdx
import json
from json import JSONEncoder
from datetime import date, datetime
import pandas as pd

from shared import get_epds, get_folder, get_full_epd_str
import uuid

def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default
JSONEncoder.default = _default

# epds assigned to parts
# parts make up assemblies
# assemblies are filled with results based on a model
# assemblies are grouped into an lca



# start the plugin

# plugin reads a list of queries from a database - eg all walls with structural amterial = STB
# plugin reads a list of assemblies mapped to the list of queries - eg query above -> reinforced concrete wall (assembly)

# plugin reads from assembly which quantity value needs to be read from the elements in revit - eg volume
# plugin generate a new assembly instance from the assembly catalogue and assigns the read quantity of the elements to the quantity property of the assembly 
# plugin writes all the IDs of revit elements to the results property of the assembly
# plugin reads from assembly which parts are making up that assembly
# plugin reads from the parts which unit the part needs and convert if necessary
# plugin reads from the epd in the part which environmental indicators we calculate
# plugin create a new parts instance and assign it to the assembly instance´s parts collection
# plugin writes the results values based on the assembly quantity in the epds for all parts in the parts collection of the assembly



class assembly():
    description = ""
    id = ""
    name = ""
    parts = dict()    # dictionary of dictionaries key = id of part : value = part object
    unit = ""  # the unit that will be used as a denominator for this assembly

    # optional properties #
    classification = tuple()  # e.g. code, name, system of classification 
    quantity = 1  # results of the calculation - can be 0 if the assembly is saved "on its own" as a catalogue item
    members = list()  # list of dictionary objects, key = id of object : value = reference to object element    <- here is where the ID of revit elements would be stored

    def __init__(self):
        pass

    def to_json(self):
        return json.dumps(self, default= lambda o : o.__dict__)

class part():
    id = str
    name = str
    partQuantityFactor = float # factor to apply to the assembly quantity
    partUnit = str
    conversion = dict
    """conversion value from the assembly unit to the part unit: 
        grammage (m2 to kg), 
        linear_density (m to kg), 
        gross_density (m3 to kg),  
        section_area (m to m2),
        thickness (m2 to m3)  """
    def __init__(self):
        pass

    def to_json(self):
        return json.dumps(self, default= lambda o : o.__dict__)
    



class epdPart(part):
    epdSource = dict    # epd id : epd as epdx json. need to write down all the values for full transparency, an epd can be updated at a later date. 

    def __init__(self):
        pass


class lca(dict):
    description = str
    id = str
    formatVersion = str
    lifeCycleStages = list
    location = str
    name = str
    emissionParts = dict      # dictionary of dictionaries key = id of assembly : value = assembly object
    impact_categories = list

    def __init__(self) -> None:
        pass


reinforcedConcrete = assembly()

reinforcedConcrete.description = "Reiforced concrete element, made of C30/37 concrete and 175 kg of steel per M3"
reinforcedConcrete.classification = "Structural Elements"
reinforcedConcrete.id = str(uuid.uuid4())
reinforcedConcrete.name = "Reinforced Concrete Structural"
reinforcedConcrete.unit = "M3"
reinforcedConcrete.quantity = 1


concreteid = "258b377e-ec3b-4e8c-b3fd-dda1eb370f7d"
steelid = "8565038f-5c21-48d7-94cb-958498ba9dd3"

def createEpdPart(_epd_id):
    conversions = ["linear density", "gross density", "grammage", "layer thickness"]
    output = epdPart()
    try:
        epd_str = get_full_epd_str(_epd_id)
        #converts to epdx formatted json string
        epdx_str = epdx.convert_ilcd(data = epd_str, as_type = str)
        epdx_data = json.loads(epdx_str)
    except:
        print ("id {0} not found".format(_epd_id))
        return

    output.id = _epd_id
    output.name = epdx_data['name']
    output.epdSource = {_epd_id :  epdx_data }
    output.partUnit = epdx_data['declared_unit']

    def find_conversion(_epdx, metadata):
        conversions = _epdx['conversions']
#        print("type of conversions is {0}".format(type(conversions)))
        if conversions == None:
            return 0
        for conversion in conversions:
            conv_metadata = json.loads(conversion["meta_data"])
#            print("type of conversions metadata is {0}".format(type(conv_metadata)))            
            if conv_metadata["name"] == metadata:
                return conv_metadata["value"]
        return 0
    output.conversion = dict()
    for conversion in conversions:
        output.conversion.update({conversion : find_conversion(epdx_data, conversion)})
    
    return output


concretePart = createEpdPart(concreteid)
steelPart = createEpdPart(steelid)

concretePart.partQuantityFactor = 1
steelPart.partQuantityFactor = 175

reinforcedConcrete.parts = {concretePart.id : concretePart, steelPart.id : steelPart}

#print(json.dumps(reinforcedConcrete))

