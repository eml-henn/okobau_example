# module to check if an epd is on the mysql database, and update / write data 
import mysql.connector
import epdx
import json
from datetime import date, datetime
import pandas as pd

from shared import get_epds, get_folder, get_full_epd_str

DB_NAME = 'henn_directus'
DB_TABLE = "henn_directus.products"

OKOBAU_URL = "https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/cd2bda71-760b-4fcc-8a0b-3877c10000a8"



def export_as_epdx(_epd_id):
    """query Okobau for an epd with a given id, and converts it to 
    epdx in json format
    returns a dictionary where key = epd_id : value = epdx json string
    """
    output = "no id provided - this method needs the ID of an epd from Okobau"
    if _epd_id == None:
        return output
  
    epd_id = []

    if isinstance(_epd_id, list):
        epd_id = _epd_id
    else:
        epd_id = [_epd_id]

    for id in epd_id:
        try:
            #gets the full epd data in ilcd format
            epd_str = get_full_epd_str(id)

            #converts to epdx formatted json string
            epdx_str = epdx.convert_ilcd(data = epd_str, as_type = str)

            if isinstance(output, str):
               output = {}
            
            output.update({id : epdx_str})
        except:
           print("id not found")
           continue

    return output

def update_table(_epd_id, connection):
    """queryes the table defined in DB_TABLE and checks if the product
    is already defined, and either updates the values or create a new database
    entry"""

    def data_exists():
        query = ("SELECT EXISTS(SELECT * FROM " + DB_TABLE + " WHERE epd_id = %s)")       
        control_cursor = connection.cursor()
        control_cursor.execute(query, [_epd_id])
        results = control_cursor.fetchall()
        for row in results:
            if row[0] == 1:
                control_cursor.close()
                return True
            else:
                control_cursor.close()
                return False

    epdx = export_as_epdx(_epd_id)[_epd_id]
    epdx_data = json.loads(epdx)
    epdx_name = epdx_data['name']

    epdx_source_name = "okobau"
    epdx_source_url = f"{OKOBAU_URL}/processes/{_epd_id}"
    epdx_declared_unit = epdx_data['declared_unit']
    epdx_version = epdx_data['version']
    epdx_published_date = pd.to_datetime(epdx_data['published_date'],  unit="s").date()
    epdx_valid_until = pd.to_datetime(epdx_data['valid_until'],  unit="s").date()
    epdx_standard = epdx_data['standard']
    epdx_location = epdx_data['location']
    epdx_subtype = epdx_data['subtype']

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
    
    epdx_linear_density = find_conversion(epdx_data, "linear density")
    epdx_gross_density = find_conversion(epdx_data, "gross density")
    epdx_area_density = find_conversion(epdx_data, "grammage")
    epdx_area_thickness = find_conversion(epdx_data, "layer thickness")


    query_data = {'date' : datetime.now().date(), 
                  'name' : epdx_name, 
                  'epd_id' : _epd_id,
                  'epdx_source_name' : epdx_source_name, 
                  'epdx_source_url' : epdx_source_url,
                  'epdx_declared_unit' : epdx_declared_unit,
                  'epdx_version' : epdx_version,
                  'epdx_published_date' : epdx_published_date,
                  'epdx_valid_until' : epdx_valid_until,
                  'epdx_standard' : epdx_standard,
                  'epdx_location' : epdx_location,
                  'epdx_linear_density' : epdx_linear_density,
                  'epdx_gross_density' : epdx_gross_density,
                  'epdx_area_density' : epdx_area_density,
                  'epdx_area_thickness' : epdx_area_thickness,
                  'epdx_subtype' : epdx_subtype,
                  'epdx' : epdx }

#    print(query_data)


    if data_exists():      
       query_product = "(SELECT * from " + DB_TABLE + " where epd_id = %s)"
       cursor = connection.cursor()
       cursor.execute(query_product, [_epd_id])
       results = cursor.fetchall()
       query_data_list = []
       for row in results:
           temp_dict = query_data.copy()
           temp_dict.update({'ids' : row[0]})
           query_data_list.append(temp_dict)
    
#       print(query_data_list)
       
       cursor.close()

       query = ("UPDATE " + DB_TABLE + " SET\
                date_updated= %(date)s, name= %(name)s, epd_id= %(epd_id)s, epdx= %(epdx)s, \
                source_name= %(epdx_source_name)s, \
                source_url=%(epdx_source_url)s, \
                declared_unit=%(epdx_declared_unit)s, \
                version=%(epdx_version)s, \
                published_date=%(epdx_published_date)s, \
                valid_until=%(epdx_valid_until)s, \
                standard=%(epdx_standard)s, \
                location=%(epdx_location)s, \
                linear_density=%(epdx_linear_density)s, \
                gross_density=%(epdx_gross_density)s, \
                area_density=%(epdx_area_density)s, \
                area_thickness=%(epdx_area_thickness)s, \
                subtype = %(epdx_subtype)s \
                WHERE id = %(ids)s")
       
       cursor = connection.cursor()
       cursor.executemany(query, query_data_list)


    else:
        query = ("INSERT INTO " + DB_TABLE + " (\
                date_created, name, epd_id, epdx, \
                source_name, \
                source_url, \
                declared_unit, \
                version, \
                published_date, \
                valid_until, \
                standard, \
                location, \
                linear_density, \
                gross_density, \
                area_density, \
                area_thickness, \
                subtype )" 
        		"VALUES( %(date)s, %(name)s, %(epd_id)s, %(epdx)s, \
                %(epdx_source_name)s, \
                %(epdx_source_url)s, \
                %(epdx_declared_unit)s, \
                %(epdx_version)s, \
                %(epdx_published_date)s, \
                %(epdx_valid_until)s, \
                %(epdx_standard)s, \
                %(epdx_location)s, \
                %(epdx_linear_density)s, \
                %(epdx_gross_density)s, \
                %(epdx_area_density)s, \
                %(epdx_area_thickness)s, \
                %(epdx_subtype)s )")
    
        cursor = connection.cursor()
        cursor.execute(query, query_data)

    connection.commit()
    cursor.close()



if __name__ == "__main__":
	epd_id = ["30452630-b12d-43bf-b140-58e0db0ba549", "fdc99ab8-d843-44ec-a66c-92367d244321", "8565038f-5c21-48d7-94cb-958498ba9dd3"]
    
	cnx = mysql.connector.connect(user='admin', password='sophien21', 
                              host='berlin117',
                              database=DB_NAME)
    
	if not isinstance(epd_id, list):
		epd_id = [epd_id]
    
	for id in epd_id:
		update_table(id, cnx)
	cnx.close()