import streamlit as st
import time
import os
from PIL import Image
from helpers import *
st.set_page_config(page_title="Enter Statistics", page_icon="💻")
clear_cache = st.button("Clear Cache")



image = Image.open(os.path.abspath(os.path.join("catan-background.jpeg")))
st.image(image)

if clear_cache:
    # Clear values from *all* all in-memory and on-disk data caches:
    # i.e. clear values from both square and cube
    st.cache_data.clear()
    st.cache_resource.clear()


def main():
    """

    :return:
    """
    st.header('Genel Oyun Bilgileri')
    # Text inputs
    st.markdown(
        "Tüm istatistikleri kaydettikten sonra en alttaki özet tablodan"
        "girdiğiniz istatistikleri görebilirsiniz. Eğer hatalı olduğunu "
        "düşünüyorsanız kişiyi seçip tekrar güncelleyebilirsiniz. Tüm "
        "oyuncuları girdiğinizde en altta Google Sheet'e kaydetme butonu "
        "aktif olacak. Ona basarak Google Sheet'e kaydedebilirsiniz.")

    metadata = dict()
    conn = connect_for_read()
    existing_players_from_db = get_distinct_data(connection=conn, col=col_idx(
        col="asil_oyuncu"))
    # get latest game id
    metadata["game_id"] = get_latest_game_id(_connection=conn, col=col_idx(
        col="oyun_no"))
    data_author = st.selectbox("Veri Girişi Yapan:",
                               existing_players_from_db)
    metadata["data_author"] = data_author
    d = st.date_input("Oyun Tarihi", datetime.date.today())
    metadata["game_date"] = d.strftime("%Y-%m-%d")
    start_time = st.time_input("Oyun Başlangıç Saati (Yaklaşık):",
                               step=600,
                               value=datetime.datetime.now())
    metadata["game_start_time"] = start_time.strftime("%H:%M")
    end_time = st.time_input("Oyun Bitiş Saati (Yaklaşık)", step=600,
                             value=datetime.datetime.now())

    metadata["game_end_time"] = end_time.strftime("%H:%M")

    metadata["is_extension"] = 0
    metadata["game_time"] = calculate_time_diff(start_time, end_time)
    st.write('Oyun ', d, " tarihinde ", start_time, " & ", end_time,
             " aralığında oynandı.")
    locations = get_distinct_data(connection=conn, col=col_idx(
        col="oyun_yeri"))
    game_place = st.selectbox("Oyun yeri: ",
                              locations + ["Yeni yer ekle"])
    if game_place == "Yeni yer ekle":
        game_place = st.text_input("Yeni oyun yeri ekleyin: ")
        st.write(f"Oyun yeri: {game_place}")
    metadata["game_place"] = str(game_place)
    total_player = st.number_input("Toplam oyuncu sayısı:", value=4,
                                   min_value=3,
                                   max_value=4)
    metadata["total_players"] = int(total_player)
    dessert_place = get_distinct_data(connection=conn, col=col_idx(
        col="col_yeri"))
    dessert_place = set(dessert_place + ["Orta"])
    dessert_placement = st.selectbox("Çöl yeri: ", dessert_place)
    metadata["dessert_placement"] = str(dessert_placement)
    # Load existing player data from cache or create a new dictionary
    player_data = st.session_state.get("player_data", {})
    # player_data = dict()
    # Get the list of existing players
    existing_players = list(player_data.keys()) + existing_players_from_db
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
        if selected_player in st.session_state:
            player_stats = st.session_state.player_data[
                selected_player]
        else:
            player_stats = {}
        with st.form("my_form"):
            game_rank = st.radio(
                f"{selected_player} için Oyun Sırası:",
                player_stats.get("game_rank",
                                 [i for i in range(1, total_player + 1)]))

            game_point = st.number_input(f"{selected_player} için Toplam "
                                         f"Puan:",
                                         value=player_stats.get("game_point",
                                                                2),
                                         min_value=2, max_value=11)

            num_of_cities = st.number_input(
                f"{selected_player} için Toplam Şehir Sayısı:",
                player_stats.get("num_of_city", 0))

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
            color = st.radio(f"{selected_player} için Oyuncu Rengi:",
                             colors,
                             index=colors.index(
                                 player_stats.get("color", "Kırmızı")))

            largest_army = st.checkbox('Şövalye :shield:',
                                       player_stats.get("largest_army",
                                                        False),
                                       disabled=False)
            if largest_army:
                st.write("Hiçbir şey yapamıyorum, sadece gelişim alıyorum "
                         ":joy:")
            longest_road = st.checkbox('En Uzun Yol', player_stats.get(
                "longest_road",
                False))
            if longest_road and largest_army:
                st.write(f"Ooo {selected_player}, bu ne cömertlik!")

            all_harbors = ["Koyun", "Odun", "Tuğla", "Kaya", "Saman", "3x1",
                           "3x1"]

            harbors = st.multiselect("Liman Seçin: (2 tane 3x1 " \
                                     "Limanı "
                                     "varsa "
                                     "ikisini de "
                                     "seçin)",
                                     player_stats.get("harbors",
                                                      all_harbors))
            all_harbors = set(all_harbors)

            harbor_dict = {}
            for i in all_harbors:
                harbor_dict[i] = st.checkbox(f"İlk {i} limanı",
                                             )

            dice_placement = st.text_input(f"{selected_player} için Zarları "
                                           f"giriniz (, ile ayırarak):",
                                           player_stats.get(
                                               "dice_placement", "3,6,9,5,2"))
            with st.container():
                ore = st.number_input("Kaya Sayısı:", min_value=0,
                                      max_value=3, value=0)
                brick = st.number_input("Tuğla Sayısı:", min_value=0,
                                        max_value=3, value=0)
                grain = st.number_input("Saman Sayısı:", min_value=0,
                                        max_value=3, value=0)
                lumber = st.number_input("Odun Sayısı:", min_value=0,
                                         max_value=3, value=0)

                wool = st.number_input("Koyun Sayısı:", min_value=0,
                                       max_value=3, value=0)

                resources = ["Kaya" for _ in range(0, ore)] + \
                            ["Odun" for _ in range(0, lumber)] + \
                            ["Tuğla" for _ in range(0, brick)] + \
                            ["Saman" for _ in range(0, grain)] + \
                            ["Koyun" for _ in range(0, wool)]

                comment = st.text_input("Ek Yorum:")
            submitted = st.form_submit_button("Kaydet", disabled=False)
        if submitted:
            player_data[selected_player] = {
                "game_rank": int(game_rank),
                "game_point": int(game_point),
                "num_of_cities": int(num_of_cities),
                "num_of_settlements": int(num_of_settlements),
                "num_of_roads": int(num_of_roads),
                "num_of_development": int(num_of_development),
                "num_of_harbor": int(num_of_harbor),
                "harbors": str(harbors),
                "first_2_1_ore": harbor_dict["Koyun"],
                "first_2_1_brick": harbor_dict["Tuğla"],
                "first_2_1_grain": harbor_dict["Saman"],
                "first_2_1_wool": harbor_dict["Koyun"],
                "first_2_1_lumber": harbor_dict["Odun"],
                "first_3_1": harbor_dict["3x1"],
                "harbor_2_1_ore": harbor_count(harbors, "Kaya"),
                "harbor_2_1_grain": harbor_count(harbors, "Koyun"),
                "harbor_3_1": harbor_count(harbors, "3x1"),
                "harbor_2_1_lumber": harbor_count(harbors, "Odun"),
                "harbor_2_1_brick": harbor_count(harbors, "Tuğla"),
                "harbor_2_1_wool": harbor_count(harbors, "Koyun"),
                "color": str(color),
                "largest_army": int(largest_army),
                "longest_road": int(longest_road),
                "first_city": int(first_city),
                "first_settlement": int(first_settlement),
                "first_development": int(first_development),
                "dice_placement": str(dice_placement),
                "initial_resources": str(resources),
                "comment": str(comment),
                "submitted": int(submitted)
            }
            st.toast(f"Saved for {selected_player} :tada:")
            st.session_state.player_data = player_data

        counter = 0
        for player in player_data.keys():
            counter = counter + int(player_data[player]["submitted"])

        if counter == total_player:
            worksheet = connect_for_insert()
            with st.spinner("Google Sheet'e kaydetmek için bekleyin.."):
                time.sleep(2)
                st.button("Google Sheet'e kaydet.", on_click=finalize_data,
                          args=(worksheet, player_data, metadata,),
                          )



if __name__ == "__main__":
    main()
