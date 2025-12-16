import streamlit as st
from abc import ABC, abstractmethod
import pandas as pd
import pydeck as pdk

# ================== DATA ==================

destinations = {
    "🇩🇪 Германия": ["Белград", "Виена", "Мюнхен", "Хамбург"],
    "🇮🇹 Италия": ["Скопие", "Рим", "Флоренция", "Венеция"],
    "🇫🇷 Франция": ["Будапеща", "Прага", "Париж", "Лион"],
    "🇪🇸 Испания": ["Мадрид", "Барселона", "Севиля"],
    "🇬🇷 Гърция": ["Атина", "Солун", "Санторини"],
    "🇳🇱 Холандия": ["Амстердам", "Ротердам"],
    "🇵🇹 Португалия": ["Лисабон", "Порто"],
    "Балкани": ["Скопие", "Тирана", "Дубровник", "Сараево"]
}

city_info = {
    "София": {"hotel": ("Hotel Sofia Center", 70), "food": ("Българска кухня", 20), "sight": "Александър Невски", "traditional": "Шопска салата"},
    "Белград": {"hotel": ("Belgrade Inn", 65), "food": ("Сръбска скара", 22), "sight": "Калемегдан", "traditional": "Ćevapi"},
    "Виена": {"hotel": ("Vienna City Hotel", 90), "food": ("Виенски шницел", 30), "sight": "Шьонбрун", "traditional": "Sachertorte"},
    "Мюнхен": {"hotel": ("Munich Central", 95), "food": ("Немска кухня", 28), "sight": "Мариенплац", "traditional": "Bratwurst"},
    "Хамбург": {"hotel": ("Hamburg Harbor Hotel", 85), "food": ("Немска кухня", 27), "sight": "Miniatur Wunderland", "traditional": "Fischbrötchen"},
    "Скопие": {"hotel": ("Skopje Square", 60), "food": ("Македонска кухня", 18), "sight": "Каменният мост", "traditional": "Тавче гравче"},
    "Рим": {"hotel": ("Roma Centrale", 110), "food": ("Италианска паста", 35), "sight": "Колизеумът", "traditional": "Carbonara"},
    "Флоренция": {"hotel": ("Florence Art", 95), "food": ("Тосканска кухня", 32), "sight": "Санта Мария дел Фиоре", "traditional": "Bistecca alla Fiorentina"},
    "Венеция": {"hotel": ("Venice Lagoon Hotel", 100), "food": ("Италианска кухня", 34), "sight": "Площад Сан Марко", "traditional": "Sarde in Saor"},
    "Будапеща": {"hotel": ("Danube View", 85), "food": ("Унгарски гулаш", 25), "sight": "Парламентът", "traditional": "Lángos"},
    "Прага": {"hotel": ("Old Town Prague", 80), "food": ("Чешка кухня", 24), "sight": "Карловият мост", "traditional": "Svíčková"},
    "Париж": {"hotel": ("Paris Boutique", 120), "food": ("Френска кухня", 40), "sight": "Айфеловата кула", "traditional": "Coq au vin"},
    "Лион": {"hotel": ("Lyon Center Hotel", 110), "food": ("Френска кухня", 38), "sight": "Базиликата Нотр Дам дьо Фурвие", "traditional": "Quenelle"},
    "Тирана": {"hotel": ("Tirana City", 55), "food": ("Албанска кухня", 17), "sight": "Скандербег", "traditional": "Byrek"},
    "Дубровник": {"hotel": ("Adriatic View", 100), "food": ("Средиземноморска кухня", 30), "sight": "Старият град", "traditional": "Pasticada"},
    "Сараево": {"hotel": ("Sarajevo Old Town Hotel", 70), "food": ("Босненска кухня", 20), "sight": "Башчаршия", "traditional": "Ćevapi"},
    "Мадрид": {"hotel": ("Madrid Central Hotel", 105), "food": ("Испанска паеля", 35), "sight": "Плаза Майор", "traditional": "Paella"},
    "Барселона": {"hotel": ("Barcelona Beach Hotel", 95), "food": ("Испанска тапас кухня", 32), "sight": "Саграда Фамилия", "traditional": "Tapas"},
    "Севиля": {"hotel": ("Seville Historic Hotel", 90), "food": ("Андалуска кухня", 30), "sight": "Алкасар", "traditional": "Gazpacho"},
    "Атина": {"hotel": ("Athens Central", 100), "food": ("Гръцка кухня", 28), "sight": "Акропола", "traditional": "Moussaka"},
    "Солун": {"hotel": ("Thessaloniki Bay Hotel", 85), "food": ("Гръцка кухня", 25), "sight": "Бялата кула", "traditional": "Souvlaki"},
    "Санторини": {"hotel": ("Santorini Cliff Hotel", 120), "food": ("Средиземноморска кухня", 38), "sight": "Калдерата", "traditional": "Fava Santorinis"},
    "Амстердам": {"hotel": ("Amsterdam Canal Hotel", 95), "food": ("Холандска кухня", 27), "sight": "Рийксмузеум", "traditional": "Stroopwafel"},
    "Ротердам": {"hotel": ("Rotterdam Central", 90), "food": ("Холандска кухня", 25), "sight": "Markthal", "traditional": "Haring"},
    "Лисабон": {"hotel": ("Lisbon Downtown Hotel", 100), "food": ("Португалска кухня", 30), "sight": "Башня Белем", "traditional": "Bacalhau"},
    "Порто": {"hotel": ("Porto Riverside", 95), "food": ("Португалска кухня", 28), "sight": "Кулата Клеригос", "traditional": "Francesinha"}
}

city_coords = {
    "София": [42.6977, 23.3219],
    "Белград": [44.7866, 20.4489],
    "Виена": [48.2082, 16.3738],
    "Мюнхен": [48.1351, 11.5820],
    "Хамбург": [53.5511, 9.9937],
    "Скопие": [41.9981, 21.4254],
    "Рим": [41.9028, 12.4964],
    "Флоренция": [43.7696, 11.2558],
    "Венеция": [45.4408, 12.3155],
    "Будапеща": [47.4979, 19.0402],
    "Прага": [50.0755, 14.4378],
    "Париж": [48.8566, 2.3522],
    "Лион": [45.7640, 4.8357],
    "Тирана": [41.3275, 19.8187],
    "Дубровник": [42.6507, 18.0944],
    "Сараево": [43.8563, 18.4131],
    "Мадрид": [40.4168, -3.7038],
    "Барселона": [41.3851, 2.1734],
    "Севиля": [37.3891, -5.9845],
    "Атина": [37.9838, 23.7275],
    "Солун": [40.6401, 22.9444],
    "Санторини": [36.3932, 25.4615],
    "Амстердам": [52.3676, 4.9041],
    "Ротердам": [51.9225, 4.4792],
    "Лисабон": [38.7223, -9.1393],
    "Порто": [41.1496, -8.6110]
}

DISTANCE_BETWEEN_CITIES = 300

# ================== OOP ==================

class Transport(ABC):
    def __init__(self, price_per_km, speed):
        self.price_per_km = price_per_km
        self.speed = speed
    @abstractmethod
    def name(self): pass
    def travel_cost(self, distance): return distance*self.price_per_km
    def travel_time(self, distance): return distance/self.speed

class Car(Transport):
    def __init__(self): super().__init__(0.25, 80)
    def name(self): return "🚗 Кола"
class Train(Transport):
    def __init__(self): super().__init__(0.18, 100)
    def name(self): return "🚆 Влак"
class Plane(Transport):
    def __init__(self): super().__init__(0.45, 600)
    def name(self): return "✈️ Самолет"

# ================== UI ==================

st.set_page_config(page_title="Туристически планер", layout="wide", page_icon="🌍")
st.title("🌍 Интерактивен туристически планер")

st.sidebar.header("🧭 Контролен панел")
target_country = st.sidebar.selectbox("Избери дестинация", list(destinations.keys()))
cities = ["София"] + destinations[target_country]

transport_choice = st.sidebar.radio("Превоз", ["Кола", "Влак", "Самолет"])
days = st.sidebar.slider("Брой дни", 1, 15, 5)
budget = st.sidebar.number_input("Бюджет (лв)", 300, 15000, 2500)
hotel_type = st.sidebar.radio("Тип хотел", ["Бюджетен", "Среден", "Луксозен"])

if st.sidebar.button("🚀 Планирай пътуването"):
    transport = Car() if transport_choice=="Кола" else Train() if transport_choice=="Влак" else Plane()

    st.subheader("🗺️ Маршрут")
    st.write(" ➡️ ".join(cities))

    # ================== MAP ==================
    points_df = pd.DataFrame([{"lat": city_coords[c][0], "lon": city_coords[c][1]} for c in cities])
    lines_df = pd.DataFrame([
        {"from_lat": city_coords[cities[i]][0], "from_lon": city_coords[cities[i]][1],
         "to_lat": city_coords[cities[i+1]][0], "to_lon": city_coords[cities[i+1]][1]}
        for i in range(len(cities)-1)
    ])

    layer_points = pdk.Layer(
        "ScatterplotLayer",
        data=points_df,
        get_position="[lon, lat]",
        get_radius=1000,
        radius_scale=6,
        radius_min_pixels=5,
        radius_max_pixels=12,
        get_fill_color=[50,130,200],
        pickable=True
    )

    layer_lines = pdk.Layer(
        "LineLayer",
        data=lines_df,
        get_source_position="[from_lon, from_lat]",
        get_target_position="[to_lon, to_lat]",
        get_width=4,
        get_color=[215,38,61]
    )

    view_state = pdk.ViewState(latitude=points_df["lat"].mean(),
                                longitude=points_df["lon"].mean(),
                                zoom=4)

    st.pydeck_chart(pdk.Deck(layers=[layer_lines, layer_points], initial_view_state=view_state))

    # ================== DETAILS ==================
    total_food = total_hotel = 0
    for city in cities:
        info = city_info[city]
        base_price = info["hotel"][1]
        if hotel_type=="Бюджетен": hotel_price = base_price*0.7
        elif hotel_type=="Среден": hotel_price = base_price
        else: hotel_price = base_price*1.3

        with st.expander(f"📍 {city}"):
            st.markdown(f"**🏨 Хотел:** {info['hotel'][0]} – {hotel_price:.2f} лв/нощ")
            st.markdown(f"**🍽️ Храна:** {info['food'][0]} – {info['food'][1]} лв/ден")
            st.markdown(f"**🍴 Традиционна храна:** {info['traditional']}")
            st.markdown(f"**🏛️ Забележителност:** {info['sight']}")

        total_hotel += hotel_price * days
        total_food += info["food"][1] * days

    distance = DISTANCE_BETWEEN_CITIES * (len(cities)-1)
    transport_cost = transport.travel_cost(distance)
    total_cost = total_hotel + total_food + transport_cost

    st.subheader("💰 Резюме")
    st.markdown(f"{transport.name()} – транспорт: {transport_cost:.2f} лв")
    st.markdown(f"🍽️ Храна: {total_food:.2f} лв")
    st.markdown(f"🏨 Хотели: {total_hotel:.2f} лв")
    st.markdown(f"## 💵 Общи разходи: {total_cost:.2f} лв")
