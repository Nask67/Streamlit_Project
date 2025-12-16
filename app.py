import streamlit as st
import pandas as pd
import pydeck as pdk
from abc import ABC, abstractmethod
import random

# ================== CONFIG ==================

st.set_page_config(
    page_title="🌍 Туристически планер",
    page_icon="🌍",
    layout="wide"
)

# ================== DATA ==================

DESTINATIONS = {
    "🇩🇪 Германия": [
        ("Виена", "Австрийски шницел"),
        ("Мюнхен", "Баварски наденички"),
        ("Хамбург", "Рибен сандвич"),
        ("Берлин", "Къривурст"),
    ],
    "🇫🇷 Франция": [
        ("Милано", "Ризото"),
        ("Лион", "Бьоф бургиньон"),
        ("Париж", "Кроасан"),
        ("Марсилия", "Буябес"),
    ],
    "🇮🇹 Италия": [
        ("Рим", "Карбонара"),
        ("Флоренция", "Тосканска кухня"),
        ("Венеция", "Морски дарове"),
        ("Милано", "Ризото"),
    ],
    "🇪🇸 Испания": [
        ("Барселона", "Паеля"),
        ("Валенсия", "Тапас"),
        ("Мадрид", "Хамон"),
        ("Севиля", "Газпачо"),
    ],
    "🇬🇷 Гърция": [
        ("Солун", "Гирос"),
        ("Атина", "Мусака"),
        ("Каламата", "Маслини"),
    ]
}

CITY_COORDS = {
    "София": [42.6977, 23.3219],
    "Виена": [48.2082, 16.3738],
    "Мюнхен": [48.1351, 11.5820],
    "Хамбург": [53.5488, 9.9872],
    "Берлин": [52.5200, 13.4050],
    "Рим": [41.9028, 12.4964],
    "Флоренция": [43.7696, 11.2558],
    "Венеция": [45.4408, 12.3155],
    "Милано": [45.4642, 9.1900],
    "Париж": [48.8566, 2.3522],
    "Лион": [45.7640, 4.8357],
    "Марсилия": [43.2965, 5.3698],
    "Барселона": [41.3851, 2.1734],
    "Валенсия": [39.4699, -0.3763],
    "Мадрид": [40.4168, -3.7038],
    "Севиля": [37.3891, -5.9845],
    "Солун": [40.6401, 22.9444],
    "Атина": [37.9838, 23.7275],
    "Каламата": [37.0389, 22.1142],
}

HOTEL_PRICES = {
    "Бюджетен": 60,
    "Среден": 100,
    "Луксозен": 160
}

DISTANCE_BETWEEN_CITIES = 300  # км

# ================== TRANSPORT ==================

class Transport(ABC):
    def __init__(self, price_per_km, speed):
        self.price_per_km = price_per_km
        self.speed = speed

    def travel_cost(self, distance):
        return distance * self.price_per_km

    def travel_time(self, distance):
        return distance / self.speed

    @abstractmethod
    def name(self):
        pass

class Car(Transport):
    def __init__(self):
        super().__init__(0.25, 80)

    def name(self):
        return "🚗 Кола"

class Train(Transport):
    def __init__(self):
        super().__init__(0.18, 110)

    def name(self):
        return "🚆 Влак"

class Plane(Transport):
    def __init__(self):
        super().__init__(0.45, 600)

    def name(self):
        return "✈️ Самолет"

# ================== UI ==================

st.title("🌍 Интерактивен туристически планер")

st.sidebar.header("🧭 Планиране")

country = st.sidebar.selectbox(
    "Избери държава",
    list(DESTINATIONS.keys())
)

max_cities = len(DESTINATIONS[country])

num_cities = st.sidebar.slider(
    "Колко града да посетиш?",
    1,
    max_cities,
    min(3, max_cities)
)

transport_choice = st.sidebar.radio(
    "Превоз",
    ["Кола", "Влак", "Самолет"]
)

hotel_type = st.sidebar.radio(
    "Тип хотел",
    list(HOTEL_PRICES.keys())
)

days = st.sidebar.slider("Брой дни", 2, 20, 7)
budget = st.sidebar.number_input("Бюджет (лв)", 500, 20000, 3000)

# ================== ROUTE ==================

selected_cities = ["София"] + [
    city for city, _ in DESTINATIONS[country][:num_cities]
]

st.subheader("🗺️ Маршрут")
st.write(" ➡️ ".join(selected_cities))

# ================== MAP ==================

points = pd.DataFrame([
    {"lat": CITY_COORDS[c][0], "lon": CITY_COORDS[c][1]}
    for c in selected_cities
])

lines = pd.DataFrame([
    {
        "from_lon": CITY_COORDS[selected_cities[i]][1],
        "from_lat": CITY_COORDS[selected_cities[i]][0],
        "to_lon": CITY_COORDS[selected_cities[i+1]][1],
        "to_lat": CITY_COORDS[selected_cities[i+1]][0],
    }
    for i in range(len(selected_cities)-1)
])

layers = [
    pdk.Layer(
        "LineLayer",
        data=lines,
        get_source_position="[from_lon, from_lat]",
        get_target_position="[to_lon, to_lat]",
        get_color=[215, 38, 61],
        get_width=4
    ),
    pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position="[lon, lat]",
        get_radius=1000,
        radius_scale=6,
        radius_min_pixels=4,
        radius_max_pixels=12,
        get_fill_color=[50, 130, 200],
        pickable=True
    )
]

view_state = pdk.ViewState(
    latitude=points["lat"].mean(),
    longitude=points["lon"].mean(),
    zoom=4
)

st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state))

# ================== DETAILS ==================

st.subheader("📍 Детайли по градове")

hotel_price = HOTEL_PRICES[hotel_type]
food_price = 30

total_food = 0
total_hotel = 0

for city in selected_cities[1:]:
    food = next(
        food for c, food in DESTINATIONS[country] if c == city
    )
    with st.expander(city):
        st.write(f"🏨 **{hotel_type} хотел:** {hotel_price} лв/нощ")
        st.write(f"🍽️ **Традиционна храна:** {food}")
        st.write("🏛️ Забележителности: исторически център")

    total_food += food_price * days
    total_hotel += hotel_price * days

# ================== SUMMARY ==================

transport = (
    Car() if transport_choice == "Кола"
    else Train() if transport_choice == "Влак"
    else Plane()
)

distance = DISTANCE_BETWEEN_CITIES * (len(selected_cities) - 1)
transport_cost = transport.travel_cost(distance)
travel_time = transport.travel_time(distance)

total_cost = total_food + total_hotel + transport_cost

st.subheader("💰 Резюме")

st.write(f"{transport.name()} – {transport_cost:.2f} лв")
st.write(f"🏨 Хотели: {total_hotel:.2f} лв")
st.write(f"🍽️ Храна: {total_food:.2f} лв")
st.write(f"⏱️ Време за пътуване: {travel_time:.1f} часа")

st.markdown("---")
st.markdown(f"## 💵 Общо: **{total_cost:.2f} лв**")

if total_cost <= budget:
    st.success("✅ В рамките на бюджета")
else:
    st.error("❌ Над бюджета")

st.info(f"🎲 Случайно събитие: {random.choice(['🎉 Фестивал', '🌧️ Лошо време', '💸 Отстъпка'])}")
