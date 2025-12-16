import streamlit as st
from abc import ABC, abstractmethod
import random
import pandas as pd

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

# ================== UI ==================

st.set_page_config(page_title="Туристически планер", layout="wide")
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
    df = pd.DataFrame([{"lat": city_coords[c][0], "lon": city_coords[c][1]} for c in cities])
    st.map(df)

    st.subheader("🏙️ Спирки")
    total_food, total_hotel = 0, 0

    progress = st.progress(0)

    for i, city in enumerate(cities):
        info = city_info[city]
        with st.expander(f"📍 {city}"):
            st.write(f"🏨 {info['hotel'][0]} – {info['hotel'][1]} лв/нощ")
            st.write(f"🍽️ {info['food'][0]} – {info['food'][1]} лв/ден")
            st.write(f"🏛️ {info['sight']}")

        total_food += info["food"][1] * days
        total_hotel += info["hotel"][1] * days
        progress.progress((i + 1) / len(cities))

    total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(total_distance)
    travel_time = transport.travel_time(total_distance)

    total_cost = total_food + total_hotel + transport_cost

    st.subheader("💰 Резюме")
    st.write(f"{transport.name()} – {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна: {total_food:.2f} лв")
    st.write(f"🏨 Хотели: {total_hotel:.2f} лв")
    st.write(f"⏱️ Време за пътуване: {travel_time:.1f} часа")

    st.markdown("---")
    st.write(f"## 💵 Общо: **{total_cost:.2f} лв**")

    if total_cost <= budget * 0.8:
        st.success("💚 Отличен бюджет – пътуваш спокойно")
    elif total_cost <= budget:
        st.warning("🟡 На ръба, но става")
    else:
        st.error("🔴 Над бюджета")

    event = random.choice([
        "🎉 Попадна на местен фестивал!",
        "🌧️ Лошо време – повече музеи",
        "💸 Отстъпка в хотел!"
    ])

    st.info(f"🎲 Случайно събитие: {event}")

    st.subheader("⭐ Оцени пътуването")
    st.slider("Колко ти хареса?", 1, 5)
