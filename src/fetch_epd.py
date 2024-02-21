import json

from shared import get_full_epd, get_folder


def get_epd_by_id(uuid: str):
    """Fetches the data of a specific EPD given its UUID"""
    data = get_full_epd(uuid)

    print(json.dumps(data, indent=4))


if __name__ == '__main__':

#    epd_id = "8be9edb5-c5b9-4be1-bfb8-b096f24a183b"
#    get_epd_by_id(epd_id)
    epd_id = "c23b2987-776d-4d55-91c7-5f2a0f2c50f1"
    get_epd_by_id(epd_id)

