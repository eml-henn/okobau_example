# module to check if an epd is on the mysql database, and update / write data 
import mysql.connector
import epdx
import json
from datetime import date, datetime

from shared import get_epds, get_folder, get_full_epd_str

DB_NAME = 'henn_directus'
DB_TABLE = "henn_directus.products"

epd_id = "c23b2987-776d-4d55-91c7-5f2a0f2c50f1"


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
    print("EPDX data:")
    print(epdx_data)
    epdx_name = epdx_data['name']
    print("###################################")
    print("epdx name is {0}".format(epdx_name))

    query_data = {'date' : datetime.now().date(), 'name' : epdx_name, 'epd_id' : _epd_id, 'epdx' : epdx }

    print(query_data)


    if data_exists():      
       query_product = "(SELECT * from " + DB_TABLE + " where epd_id = '%s')"
       cursor = connection.cursor()
       cursor.execute(query_product, [_epd_id])
       results = cursor.fetchall()
       epd_ids = [row[0] for row in results]
       query_data.update({'ids' : epd_ids})
       cursor.close()

       query = ("INSERT INTO " + DB_TABLE + " (date_created, name, epd_id, epdx) \
                VALUES( %(date)s, %(name)s, %(epd_id)s, %(epdx)s) \
                SELECT id, %(ids)s \
                ON DUPLICATE KEY UPDATE date_updated = %(date)s, name = '%(name)s', \
                epd_id = '%(epd_id)s', epdx = '%(epdx)s' ")
       
    else:
        query = ("INSERT INTO " + DB_TABLE + " (date_created, name, epd_id, epdx) \
        VALUES( %(date)s, %(name)s, %(epd_id)s, %(epdx)s)")
    
    cursor = connection.cursor()
    cursor.execute(query, query_data)

    connection.commit()
    cursor.close()



cnx = mysql.connector.connect(user='admin', password='sophien21', 
                              host='berlin117',
                              database=DB_NAME)
    
update_table(epd_id, cnx)


"""
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cnx.close()

"""

cnx.close()