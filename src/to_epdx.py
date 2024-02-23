import epdx
import json

from shared import get_epds, get_folder, get_full_epd_str


def to_epdx(_epd_id = None):
    """Get EPDs from Ökobau and turn them into EPDx"""

    folder = get_folder(__file__, "epdx_data")

    raw_folder = get_folder(__file__, "epd_raw_data")

    epd_id = []

    if _epd_id == None:
        data = get_epds()

        for _epd in data.get("data"):
            epd_id.append(_epd.get('uuid'))
    
    else:
        if isinstance(_epd_id, list):
            epd_id = _epd_id
        else:
            epd_id.append(_epd_id)

    
    for _epd in epd_id:
        print(f"\nEPD {_epd}")

        # Get full EPD from Ökobau
        epd_str = get_full_epd_str(_epd)

        # save full EPD to disk
        ((raw_folder / f"{_epd}.epd.json")
         .write_text(json.dumps(epd_str, indent=4)))


        # Turn EPD into EPDx JSON string that can be saved to disk.
        epdx_str = epdx.convert_ilcd(data = epd_str,
                                     as_type= str)
        ((folder / f"{_epd}.epdx.json")
         .write_text(epdx_str))

        # Turn EPD into EPDx dict
        epdx_dict = epdx.convert_ilcd(epd_str)
        print('EPDx Dict')
        print(epdx_dict)

        # Turn EPD into an EPDx Pydantic Class
        epdx_pydantic = epdx.convert_ilcd(epd_str,
                                          as_type=epdx.EPD)
        print('\nEPDx Pydantic')
        print(epdx_pydantic)
        print("---------\n")


if __name__ == "__main__":
    to_epdx("c23b2987-776d-4d55-91c7-5f2a0f2c50f1")
