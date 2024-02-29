import json

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



class assembly:
    description = str
    id = str
    name = str
    parts = dict    # dictionary of dictionaries key = id of part : value = part object
    unit = str  # the unit that will be used as a denominator for this assembly

    # optional properties #
    classification = tuple  # e.g. code, name, system of classification 
    quantity = float  # results of the calculation - can be 0 if the assembly is saved "on its own" as a catalogue item
    members = list  # list of dictionary objects, key = id of object : value = reference to object element    <- here is where the ID of revit elements would be stored

    def __init__(self) -> None:
        pass

class part:
    id = str
    name = str
    parent = assembly
    partQuantityFactor = float # factor to apply to the assembly quantity
    partQuantity = parent.quantity * partQuantityFactor
    partUnit = str
    conversion = dict
    """conversion value from the assembly unit to the part unit: 
        grammage (m2 to kg), 
        linear_density (m to kg), 
        gross_density (m3 to kg),  
        section_area (m to m2),
        thickness (m2 to m3)  """
    def __init__(self) -> None:
        pass

class epdPart(part):
    epdSource = dict    # epd id : epd as epdx json. need to write down all the values for full transparency, an epd can be updated at a later date. 

    def __init__(self) -> None:
        pass

class lca:
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