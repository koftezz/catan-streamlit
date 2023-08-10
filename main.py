import datetime
import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.title("Catan Statistics App")

st.sidebar.success("İstatistikleri Gör")


def controls(player_dict: dict):
    msg = ""
    for player in player_dict.keys():
        stats = player_dict[player]
        if stats["first_city"] and int(stats["num_of_cities"]) < 1:
            msg += f"f{player} can't have first city with " \
                   f"{str(stats['num_of_cities'])}"
            break
    if len(msg) > 0:
        st.toast(msg)


def main():
    st.header('Genel Oyun Bilgileri')
    # Text inputs

    # Allow user to select an existing player or create a new one
    data_author = st.selectbox("Veri Girişi Yapan:",
                               ["Batuhan", "Alperen"])

    d = st.date_input("Oyun Tarihi", datetime.date.today())
    start_time = st.time_input("Oyun Başlangıç Saati (Yaklaşık):",
                               step=600,
                               value=datetime.datetime.now())
    end_time = st.time_input("Oyun Bitiş Saati (Yaklaşık)", step=600,
                             value=datetime.datetime.now())
    st.write('Oyun ', d, " tarihinde ", start_time, " & ", end_time,
             " aralığında oynandı.")
    locations = ["Bodrum", "ÇatoMel", "Tunçkan"]
    game_place = st.selectbox("Oyun yeri: ",
                              locations + ["Yeni yer ekle"])
    if game_place == "Yeni yer ekle":
        new_game_place = st.text_input("Yeni oyun yeri ekleyin: ")
        st.write(f"Oyun yeri: {new_game_place}")

    total_player = st.number_input("Toplam oyuncu sayısı", value=4,
                                   min_value=3,
                                   max_value=4)
    # Load existing player data from cache or create a new dictionary
    player_data = st.session_state.get("player_data", {})

    # Get the list of existing players
    existing_players = list(player_data.keys()) + ["Alp", "Batu"]
    existing_players = list(set(existing_players))

    # Allow user to select an existing player or create a new one
    selected_player = st.selectbox("Oyuncu seç ya da yeni oyuncu ekle:",
                                   list(set(existing_players)) + ["Yeni "
                                                                  "oyuncu "
                                                                  "ekle"])

    if selected_player == "Yeni oyuncu ekle":
        new_player_name = st.text_input("Oyuncunun adını giriniz:")
        if new_player_name:
            selected_player = new_player_name

    st.write(f"Seçilen oyuncu: {selected_player}")
    if selected_player:
        st.subheader(f"{selected_player} için istatistikleri giriniz")
        with st.form("my_form", clear_on_submit=True):
            player_stats = player_data.get(selected_player, {})
            games_rank = st.number_input(
                f"{selected_player} için Oyun Sırası:",
                value=player_stats.get("games_rank", 1),
                min_value=1,
                max_value=4)

            num_of_cities = st.number_input(
                f"{selected_player} için Toplam Şehir Sayısı:",
                player_stats.get("num_of_city", 0))
            st.write("Girilen toplam şehir sayısı: ", num_of_cities)
            first_city = st.checkbox('İlk Şehir')
            num_of_settlements = st.number_input(f"{selected_player} için "
                                                 f"Toplam "
                                                 f"Köy Sayısı",
                                                 player_stats.get(
                                                     "num_of_settlement", 0))
            first_settlement = st.checkbox('İlk Köy')
            num_of_roads = st.number_input(
                f"{selected_player} için Toplam Yol "
                f"Sayısı",
                player_stats.get(
                    "num_of_road", 2))

            num_of_development = st.number_input(f"{selected_player} için "
                                                 f"Toplam "
                                                 f"Gelişim Kartı Sayısı",
                                                 player_stats.get(
                                                     "num_of_dev_cards", 0))

            first_development = st.checkbox('İlk Gelişim Kartı')

            num_of_harbor = st.number_input(f"{selected_player} için Toplam "
                                            f"Liman "
                                            f"Sayısı",
                                            player_stats.get(
                                                "num_of_harbor", 0))
            colors = ["Kırmızı", "Turuncu", "Beyaz", "Mavi"]
            color = st.selectbox(f"{selected_player} için Oyuncu Rengi:",
                                 colors,
                                 index=colors.index(
                                     player_stats.get("color", "Kırmızı")))

            if int(num_of_development) < 3:
                st.warning(f"Şövalye için "
                           f"{int(num_of_development)} adet kart yetersiz.")
                largest_army = st.checkbox('Şövalye :shield:', disabled=True)
            else:
                largest_army = st.checkbox('Şövalye :shield:')
                if largest_army:
                    st.write("Hiçbir şey yapamıyorum, sadece gelişim alıyorum "
                             ":joy:")
            longest_road = st.checkbox('En Uzun Yol')
            if longest_road and largest_army:
                st.write(f"Ooo {selected_player}, bu ne cömertlik!")

            if int(num_of_harbor) > 0:
                st.multiselect("Liman Seçin: (2 tane 3x1 Limanı varsa "
                               "ikisini de "
                               "seçin",
                               ["Koyun", "Odun", "Tuğla", "Kaya", "3x1", "3x1"]
                               )

            # Update player data
            submitted = st.form_submit_button("Kaydet")
            if submitted:
                player_data[selected_player] = {
                    "games_rank": int(games_rank),
                    "num_of_cities": int(num_of_cities),
                    "num_of_settlements": int(num_of_settlements),
                    "num_of_roads": int(num_of_roads),
                    "num_of_development": int(num_of_development),
                    "num_of_harbor": int(num_of_harbor),
                    "color": str(color),
                    "largest_army": largest_army,
                    "longest_road": longest_road,
                    "first_city": first_city,
                    "first_settlement": first_settlement,
                    "first_development": first_development,
                    "submitted": submitted
                }
                st.toast(f"Saved for {selected_player} :tada:")
                st.session_state.player_data = player_data

        counter = 0
        for player in player_data.keys():
            counter = counter + int(player_data[player]["submitted"])

        if counter == total_player:
            st.button("Google Sheet'e kaydet.", on_click=controls,
                      kwargs={"player_dict": player_data})

        st.table(player_data)

def get_db_connection():

    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    conn = connect(credentials=credentials)
    return conn

def get_data(connection):

    @st.cache_resource(ttl=600)
    def run_query(query):
        rows = connection.execute(query, headers=1)
        rows = rows.fetchall()
        return rows


    sheet_url = st.secrets["private_gsheets_url"]
    rows = run_query(f'SELECT * FROM "{sheet_url}"')

    # Print results.
    for row in rows:
        st.write(f"{row.Kazanan} has a :{row.Tarih}:")

if __name__ == "__main__":
    main()


