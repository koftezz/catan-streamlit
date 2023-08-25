import pandas as pd
import numpy as np

import datetime
import streamlit as st
import gspread

from google.oauth2 import service_account
from streamlit_gsheets import GSheetsConnection



def col_idx(col: str) -> int:
    """

    :param col:
    :return:
    """
    col_dict = {
        "oyun_no": 1,
        "tarih": 2,
        "asil_oyuncu": 3,
        "col_yeri": 37,
        "oyun_yeri": 38,
    }
    return col_dict[col]


def controls(player_dict: dict):
    """

    :param player_dict:
    :return:
    """
    msg = ""
    for player in player_dict.keys():
        stats = player_dict[player]
        if stats["first_city"] and int(stats["num_of_cities"]) < 1:
            msg += f"f{player} can't have first city with " \
                   f"{str(stats['num_of_cities'])}"
            break
    if len(msg) > 0:
        st.toast(msg)

def harbor_count(lst, x):
    count = 0
    for ele in lst:
        if ele == x:
            count = count + 1
    return count


def calculate_time_diff(start_time: datetime.time,
                        end_time: datetime.time):
    """

    :param start_time:
    :param end_time:
    :return:
    """
    date1 = datetime.datetime(2023, 8, 23)
    date2 = datetime.datetime(2023, 8, 24)

    # Combine date and time
    datetime1 = datetime.datetime.combine(date1, start_time)
    datetime2 = datetime.datetime.combine(date2, end_time)

    # Calculate the time difference
    time_difference = datetime2 - datetime1

    # Convert time difference to minutes
    return int(time_difference.total_seconds() / 60)


def finalize_data(*args):
    """

    :param args:
    :return:
    """
    worksheet = args[0]
    player_data = args[1]
    metadata = args[2]
    mapping = col_mapping()
    columns = mapping.values()
    data = pd.DataFrame.from_dict(player_data, orient="index")
    metadata = pd.DataFrame(metadata.values(),
                            index=metadata.keys()).transpose()
    data.reset_index(inplace=True)
    data['key'] = 0
    metadata['key'] = 0
    data = data.merge(metadata, on='key', how='outer')
    data = data.drop("key", axis=1)
    data = data.rename(columns=mapping)
    data = data.reindex(columns=mapping.values())
    data["kazanan"] = \
        data.loc[data["puan"] == data["puan"].max(axis=0)].asil_oyuncu.values[
            0]
    data = data[columns]
    insert_data(ws=worksheet, data=data)
    return data


def col_mapping():
    """

    :return:
    """
    mapping = {
        "game_id": "oyun_no",
        "game_date": "tarih",
        "index": "asil_oyuncu",
        "game_rank": "sira",
        "subs_player": "yedek_oyuncu",
        "winner": "kazanan",
        "game_point": "puan",
        "color": "renk",
        "num_of_cities": "sehir_sayisi",
        "num_of_settlements": "koy_sayisi",
        "num_of_roads": "yol_sayisi",
        "num_of_development": "gelisim_sayisi",
        "first_development": "ilk_gelisim",
        "first_city": "ilk_sehir",
        "first_settlement": "ilk_koy",
        "num_of_harbor": "liman_sayisi",
        "initial_resources": "ilk_kaynaklar",
        "cashier": "kasa",
        "game_time": "sure",
        "is_extension": "extension",
        "game_start_time": "baslangic_saat",
        "longest_road": "en_uzun_yol",
        "largest_army": "sovalye",
        "first_2_1_ore": "ilk_2_1_kaya",
        "first_2_1_brick": "ilk_2_1_tugla",
        "first_2_1_grain": "ilk_2_1_saman",
        "first_2_1_wool": "ilk_2_1_koyun",
        "first_2_1_lumber": "ilk_2_1_odun",
        "first_3_1": "ilk_3_1",
        "harbor_2_1_ore": "liman_2_1_kaya",
        "harbor_2_1_grain": "liman_2_1_saman",
        "harbor_3_1": "liman_3_1",
        "harbor_2_1_lumber": "liman_2_1_odun",
        "harbor_2_1_brick": "liman_2_1_tugla",
        "harbor_2_1_wool": "liman_2_1_koyun",
        "dice_placement": "zar",
        "dessert_placement": "col_yeri",
        "game_place": "oyun_yeri",
        "comment": "ek_not",
        "data_author": "veri_sahibi"
    }
    return mapping


def insert_data(ws: gspread.Spreadsheet, data: pd.DataFrame):
    """

    :param ws:
    :param data:
    :return:
    """
    data = data.fillna(0)
    for col in data.columns:
        if data[col].dtype == np.int64:
            data[col] = data[col].astype(int)
    for row in data.iterrows():
        ws.append_row(list(row[1].values))
    msg = "Data inserted successfully."
    st.toast(msg)


def connect_for_insert():
    """

    :return:
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope,
    )
    client = gspread.authorize(credentials)
    sh = client.open_by_key('1DGKLNqnlpgHX9E-FZpEzapUswjO3lf8RLywmEptsYDE')
    worksheet = sh.get_worksheet(0)
    return worksheet


def connect_for_read():
    conn = st.experimental_connection("gsheets", type=GSheetsConnection,
                                      ttl=600, kwargs={"show_spinner": False})
    return conn


def get_distinct_data(connection: st.experimental_connection, col: int):
    # increase index
    col = col - 1
    df = connection.read(spreadsheet=st.secrets["private_gsheets_url"],
                         usecols=[col])
    values = list(df.iloc[:, 0].dropna().unique())
    return values


def get_latest_game_id(_connection: st.experimental_connection, col: int):
    # increase index
    col = col - 1
    df = _connection.read(spreadsheet=st.secrets["private_gsheets_url"],
                          usecols=[col])
    values = list(df.iloc[:, 0].dropna().unique())
    return max(values) + 1
