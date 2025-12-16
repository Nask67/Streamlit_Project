import streamlit as st
from abc import ABC, abstractmethod
import pandas as pd
import random
import pydeck as pdk

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"],
    "България → Италия": ["София", "Скопие", "Рим", "Флоренция"],
    "България → Франция": ["София", "Будапеща", "Прага", "Париж"],
    "Балканска обиколка": ["София", "Скопие", "Тирана", "Дубровник"]
}

city_info = {
    "София": {"hotel": ("Hotel Sofia Center", 70), "food": ("Българска кухня", 20), "sight": "Александър Невски"},
    "Белград": {"hotel": ("Belgrade Inn", 65), "food": ("Сръбска скара", 22), "sight": "Калемегдан"},
    "Виена": {"hotel": ("Vienna City Hotel", 90), "food": ("Виенски шницел", 30), "sight": "Шьонбрун"},
    "Мюнхен": {"hotel": ("Munich Central", 95), "food": ("Немска кухня", 28), "sight": "Мариенплац"},
    "Скопие": {"hotel": ("Skopje Square", 60), "food": ("Македонска кухня", 18), "sight": "Каменният мост"},
    "Рим": {"hotel": ("Roma Centrale", 110), "food": ("Италианска паста", 35), "sight": "Колизеумът"},
    "Флоренция": {"hotel": ("Florence Art", 95), "food": ("Тосканска кухня", 32), "sight": "Санта Мария дел Фиоре"},
    "Будапеща": {"hotel": ("Danube View", 85), "food": ("Унгарски гулаш", 25), "sight": "Парламентът"},
    "Прага": {"hotel": ("Old Town Prague", 80), "food": ("Чешка кухня", 24), "sight": "Карловият мост"},
    "Париж": {"hotel": ("Paris Boutique", 120), "food": ("Френска кухня", 40), "sight": "Айфеловата кула"},
    "Тирана": {"hotel": ("Tirana City", 55), "food": ("Албанска кухня", 17), "sight": "Скандербег"},
    "Дубровник": {"hotel": ("Adriatic View", 100), "food": ("Средиземноморска кухня", 30), "sight": "Старият град"}
}

city_coords = {
    "София": [42.6977, 23.3219],
    "Белград": [44.7866, 20.4489],
    "Виена": [48.2082, 16.3738],
    "Мюнхен": [48.1351, 11.5820],
    "Скопие": [41.9981, 21.4254],
    "Рим": [41.9028, 12.4964],
    "Флоренция": [43.7696, 11.2558],
    "Будапеща": [47.4979, 19.0402],
    "Прага": [50.0755, 14.4378],
    "Париж": [48.8566, 2.3522],
    "Тирана": [41.3275, 19.8187],
    "Дубровник": [42.6507, 18.0944]
}

DISTANCE_BETWEEN_CITIES = 300

# ================== OOP ==================

class Transport(ABC):
    def __init__(self, price_per_km, speed):
        self.price_per_km = price_per_km
        self.speed = speed

    @abstractmethod
    def name(self):
        pass

    def travel_cost(self, distance):
        return distance * self.price_per_km

    def travel_time(self, distance):
        return distance / self.speed

class Car(Transport):
    def __init__(self):
        super().__init__(0.25, 80)
    def name(self):
        return "🚗 Кола"

class Train(Transport):
    def __init__(self):
        super().__init__(0.18, 100)
    def name(self):
        return "🚆 Влак"

class Plane(Transport):
    def __init__(self):
        super().__init__(0.45, 600)
    def name(self):
        return "✈️ Самолет"

# ================== THEME ==================

# Инициализация на session_state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Toggle за тъмна/светла тема
dark_mode = st.sidebar.checkbox("🌙 Тъмна тема", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# Цветови схеми
if st.session_state.dark_mode:
    PRIMARY_COLOR = "#d1d1d1"
    SECONDARY_COLOR = "#222222"
    ACCENT_COLOR = "#ff4b5c"
    BG_COLOR = "#0f0f0f"
    TEXT_COLOR = "white"
else:
    PRIMARY_COLOR = "#0f4c75"
    SECONDARY_COLOR = "#3282b8"
    ACCENT_COLOR = "#d7263d"
    BG_COLOR = "#f0f4f8"
    TEXT_COLOR = "black"

# Прилагане на CSS
st.markdown(
    f"""
    <style>
        .reportview-container {{
            background-color: {BG_COLOR};
            color: {TEXT_COLOR};
        }}
        .sidebar .sidebar-content {{
            background-color: {SECONDARY_COLOR};
            color: white;
        }}
        .stButton>button {{
            background-color: {ACCENT_COLOR};
            color: white;
        }}
        h1 {{
            color: {PRIMARY_COLOR};
        }}
    </style>
    """, unsafe_allow_html=True
)

# ================== UI ==================

st.title("🌍 Интерактивен туристически планер")

st.sidebar.header("🧭 Контролен панел")
route_choice = st.sidebar.selectbox("Маршрут", list(routes.keys()))
transport_choice = st.sidebar.radio("Превоз", ["Кола", "Влак", "Самолет"])
days = st.sidebar.slider("Брой дни", 1, 10, 4)
budget = st.sidebar.number_input("Бюджет (лв)", 300, 5000, 1500)

if st.sidebar.button("🚀 Планирай пътуването"):
    cities = routes[route_choice]
    transport = Car() if transport_choice == "Кола" else Train() if transport_choice == "Влак" else Plane()

    st.subheader("🗺️ Маршрут")
    st.write(" ➡️ ".join(cities))

    # MAP
    points_df = pd.DataFrame([{"lat": city_coords[c][0], "lon": city_coords[c][1]} for c in cities])
    lines_df = pd.DataFrame([
        {"from_lat": city_coords[cities[i]][0],
         "from_lon": city_coords[cities[i]][1],
         "to_lat": city_coords[cities[i + 1]][0],
         "to_lon": city_coords[cities[i + 1]][1]} for i in range(len(cities) - 1)
    ])
    layer_points = pdk.Layer(
        "ScatterplotLayer",
        data=points_df,
        get_position="[lon, lat]",
        get_radius=1000,
        radius_scale=6,
        radius_min_pixels=4,
        radius_max_pixels=12,
        get_fill_color=[50, 130, 200] if st.session_state.theme=="light" else [200,200,255],
        pickable=True,
    )
    layer_lines = pdk.Layer(
        "LineLayer",
        data=lines_df,
        get_source_position="[from_lon, from_lat]",
        get_target_position="[to_lon, to_lat]",
        get_width=4,
        get_color=[215, 38, 61] if st.session_state.theme=="light" else [255,100,100],
    )
    view_state = pdk.ViewState(latitude=points_df["lat"].mean(), longitude=points_df["lon"].mean(), zoom=4)
    st.pydeck_chart(pdk.Deck(layers=[layer_lines, layer_points], initial_view_state=view_state))

    # DETAILS
    total_food = total_hotel = 0
    progress = st.progress(0)
    for i, city in enumerate(cities):
        info = city_info[city]
        with st.expander(f"📍 {city}"):
            st.markdown(f"**🏨 Хотел:** {info['hotel'][0]} – {info['hotel'][1]} лв/нощ")
            st.markdown(f"**🍽️ Храна:** {info['food'][0]} – {info['food'][1]} лв/ден")
            st.markdown(f"**🏛️ Забележителност:** {info['sight']}")
        total_food += info["food"][1] * days
        total_hotel += info["hotel"][1] * days
        progress.progress((i + 1) / len(cities))

    distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(distance)
    travel_time = transport.travel_time(distance)
    total_cost = total_food + total_hotel + transport_cost

    st.subheader("💰 Резюме")
    st.markdown(f"**{transport.name()}** – {transport_cost:.2f} лв")
    st.markdown(f"🍽️ Храна: {total_food:.2f} лв")
    st.markdown(f"🏨 Хотели: {total_hotel:.2f} лв")
    st.markdown(f"⏱️ Време за пътуване: {travel_time:.1f} часа")

    st.markdown("---")
    st.markdown(f"## 💵 Общо: **{total_cost:.2f} лв**")
    if total_cost <= budget * 0.8: st.success("💚 Отличен бюджет")
    elif total_cost <= budget: st.warning("🟡 На ръба")
    else: st.error("🔴 Над бюджета")

    st.info(f"🎲 Случайно събитие: {random.choice(['🎉 Фестивал', '🌧️ Лошо време', '💸 Отстъпка'])}")
    st.subheader("⭐ Оцени пътуването")
    st.slider("Колко ти хареса?", 1, 5)
