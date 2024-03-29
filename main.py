import csv
import json

import requests
from bs4 import BeautifulSoup

FREE_FIT_SEARCH_URL = 'https://freefit.co.il/Master.asmx/SearchClubList'
FREE_FIT_CLUB_URL = 'https://freefit.co.il/CLUBS/?CLUB='

if __name__ == '__main__':
    search_clubs_result = requests.post(FREE_FIT_SEARCH_URL,
                                        data=json.dumps(
                                            {"CompanyID": 0, "subcategoryId": "-1", "area": "-1", "CompanyName": "",
                                             "freeText": ""}),
                                        headers={'X-Requested-With': 'XMLHttpRequest',
                                                 'content-type': 'application/json; charset=UTF-8'})

    clubs_data = search_clubs_result.json()
    clubs = set()
    for club_data in clubs_data['d']:
        clubs.add((f'{FREE_FIT_CLUB_URL}{club_data["Id"]}', club_data["Name"]))

    rows = set()
    for i, (club_link, club_name) in enumerate(clubs):
        print(f"Club {i}/{len(clubs)}")
        club_page = requests.get(club_link)
        soup = BeautifulSoup(club_page.text, features="html.parser")
        map_links = soup.select('a[href*=\'maps\']')
        for map_link in map_links:
            try:
                point_value = None
                if "@" in map_link.attrs['href']:
                    point_value = map_link.attrs['href']
                else:
                    for key in map_link.attrs.keys():
                        if key.startswith("@"):
                            point_value = key

                if not point_value:
                    continue

                point = point_value.split('@')[1].split('z')[0].split(',')

                lon = point[1]
                lat = point[0]
                rows.add((lon, lat, f'{club_name}\n{club_link}'))
            except Exception as e:
                print(f"Failed to parse {map_link}")
                pass

    header = ['lon', 'lat', 'title']
    with open('map.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
