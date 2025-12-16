import streamlit as st
import pandas as pd
import pydeck as pdk
from abc import ABC, abstractmethod
import random

# ================== CONFIG ==================

st.set_page_config(
    page_title="🌍 Туристически планер",
    page_icon="🧭",
    layout="wide"
)

# ================== STYLE ==================

# Всички снимки ще са с еднаква височина и обектът ще се побира добре
st.markdown("""
<style>
img {
    max-height: 220px;
    object-fit: cover;
}
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================

DESTINATIONS = {
    "🇩🇪 Германия": [
        ("Берлин", "Къривурст"),
        ("Мюнхен", "Баварски наденички"),
        ("Хамбург", "Рибни специалитети"),
        ("Кьолн", "Немска бира и брецели"),
    ],
    "🇫🇷 Франция": [
        ("Париж", "Кроасан и багета"),
        ("Лион", "Бьоф Бургиньон"),
        ("Марсилия", "Буябес"),
        ("Ница", "Салата Нисоаз"),
    ],
    "🇮🇹 Италия": [
        ("Рим", "Карбонара"),
        ("Флоренция", "Тосканска кухня"),
        ("Венеция", "Морски дарове"),
        ("Милано", "Ризото"),
    ],
    "🇪🇸 Испания": [
        ("Барселона", "Паеля"),
        ("Мадрид", "Хамон"),
        ("Валенсия", "Тапас"),
        ("Севиля", "Газпачо"),
    ],
    "🇬🇷 Гърция": [
        ("Солун", "Гирос"),
        ("Атина", "Мусака"),
        ("Санторини", "Морска кухня"),
    ],
    "🇦🇹 Австрия": [
        ("Виена", "Виенски шницел"),
        ("Залцбург", "Щрудел"),
        ("Инсбрук", "Алпийска кухня"),
    ],
    "🇨🇿 Чехия": [
        ("Прага", "Гулаш"),
        ("Бърно", "Чешка кухня"),
    ],
    "🇳🇱 Нидерландия": [
        ("Амстердам", "Херинга"),
        ("Ротердам", "Морски дарове"),
    ],
    "🇸🇪 Швеция": [
        ("Стокхолм", "Кюфтета"),
        ("Гьотеборг", "Рибена супа"),
    ],
    "🇭🇷 Хърватия": [
        ("Загреб", "Балканска кухня"),
        ("Сплит", "Морски дарове"),
        ("Дубровник", "Далматинска кухня"),
    ],
    "🇵🇹 Португалия": [
        ("Лисабон", "Бакаляу"),
        ("Порто", "Франсезиня"),
        ("Фаро", "Морски дарове"),
    ],
    "🇵🇱 Полша": [
        ("Варшава", "Пиероги"),
        ("Краков", "Журек"),
        ("Гданск", "Рибни ястия"),
    ],
    "🇭🇺 Унгария": [
        ("Будапеща", "Гулаш"),
        ("Дебрецен", "Унгарска наденица"),
    ],
    "🇨🇭 Швейцария": [
        ("Цюрих", "Фондю"),
        ("Женева", "Раклет"),
        ("Берн", "Швейцарска кухня"),
    ],
    "🇧🇪 Белгия": [
        ("Брюксел", "Гофрети"),
        ("Брюж", "Миди с пържени картофи"),
        ("Антверпен", "Белгийски шоколад"),
    ],
    "🇷🇴 Румъния": [
        ("Букурещ", "Сарми"),
        ("Брашов", "Трансилванска кухня"),
        ("Клуж-Напока", "Местни специалитети"),
    ],
    "🇩🇰 Дания": [
        ("Копенхаген", "Смьоребрьод"),
        ("Орхус", "Скандинавска кухня"),
    ]
}

CITY_COORDS = {
    "София": [42.6977, 23.3219],
    "Берлин": [52.5200, 13.4050],
    "Мюнхен": [48.1351, 11.5820],
    "Хамбург": [53.5488, 9.9872],
    "Кьолн": [50.9375, 6.9603],
    "Париж": [48.8566, 2.3522],
    "Лион": [45.7640, 4.8357],
    "Марсилия": [43.2965, 5.3698],
    "Ница": [43.7102, 7.2620],
    "Рим": [41.9028, 12.4964],
    "Флоренция": [43.7696, 11.2558],
    "Венеция": [45.4408, 12.3155],
    "Милано": [45.4642, 9.1900],
    "Барселона": [41.3851, 2.1734],
    "Мадрид": [40.4168, -3.7038],
    "Валенсия": [39.4699, -0.3763],
    "Севиля": [37.3891, -5.9845],
    "Солун": [40.6401, 22.9444],
    "Атина": [37.9838, 23.7275],
    "Санторини": [36.3932, 25.4615],
    "Виена": [48.2082, 16.3738],
    "Залцбург": [47.8095, 13.0550],
    "Инсбрук": [47.2692, 11.4041],
    "Прага": [50.0755, 14.4378],
    "Бърно": [49.1951, 16.6068],
    "Амстердам": [52.3676, 4.9041],
    "Ротердам": [51.9244, 4.4777],
    "Стокхолм": [59.3293, 18.0686],
    "Гьотеборг": [57.7089, 11.9746],
    "Загреб": [45.8150, 15.9819],
    "Сплит": [43.5081, 16.4402],
    "Дубровник": [42.6507, 18.0944],
    "Лисабон": [38.7223, -9.1393],
    "Порто": [41.1579, -8.6291],
    "Фаро": [37.0194, -7.9304],
    "Варшава": [52.2297, 21.0122],
    "Краков": [50.0647, 19.9450],
    "Гданск": [54.3520, 18.6466],
    "Будапеща": [47.4979, 19.0402],
    "Дебрецен": [47.5316, 21.6273],
    "Цюрих": [47.3769, 8.5417],
    "Женева": [46.2044, 6.1432],
    "Берн": [46.9480, 7.4474],
    "Брюксел": [50.8503, 4.3517],
    "Брюж": [51.2093, 3.2247],
    "Антверпен": [51.2194, 4.4025],
    "Букурещ": [44.4268, 26.1025],
    "Брашов": [45.6579, 25.6012],
    "Клуж-Напока": [46.7712, 23.6236],
    "Копенхаген": [55.6761, 12.5683],
    "Орхус": [56.1629, 10.2039],
}

CITY_IMAGES = {
    "Берлин": "http://blog.karat-s.com/nestandartni-zabelejitelnosti-berlin/",
    "Мюнхен": "https://unsplash.com/s/photos/munich-city",
    "Хамбург": "https://unsplash.com/s/photos/hamburg-city",
    "Кьолн": "https://unsplash.com/s/photos/cologne-city",

    "Париж": "https://unsplash.com/s/photos/paris-city",
    "Лион": "https://unsplash.com/s/photos/lyon-city",
    "Марсилия": "https://unsplash.com/s/photos/marseille-city",
    "Ница": "https://unsplash.com/s/photos/nice-france",

    "Рим": "https://unsplash.com/s/photos/rome-city",
    "Флоренция": "https://unsplash.com/s/photos/florence-city",
    "Венеция": "https://unsplash.com/s/photos/venice-city",
    "Милано": "https://unsplash.com/s/photos/milan-city",

    "Барселона": "https://unsplash.com/s/photos/barcelona-city",
    "Мадрид": "https://unsplash.com/s/photos/madrid-city",
    "Валенсия": "https://unsplash.com/s/photos/valencia-city",
    "Севиля": "https://unsplash.com/s/photos/seville-city",

    "Солун": "https://unsplash.com/s/photos/thessaloniki-city",
    "Атина": "https://unsplash.com/s/photos/athens-city",
    "Санторини": "https://unsplash.com/s/photos/santorini",

    "Виена": "https://unsplash.com/s/photos/vienna-city",
    "Залцбург": "https://unsplash.com/s/photos/salzburg-city",
    "Инсбрук": "https://unsplash.com/s/photos/innsbruck-city",

    "Прага": "https://unsplash.com/s/photos/prague-city",
    "Бърно": "https://unsplash.com/s/photos/brno-city",

    "Амстердам": "https://unsplash.com/s/photos/amsterdam-city",
    "Ротердам": "https://unsplash.com/s/photos/rotterdam-city",

    "Стокхолм": "https://unsplash.com/s/photos/stockholm-city",
    "Гьотеборг": "https://unsplash.com/s/photos/gothenburg-city",

    "Загреб": "https://unsplash.com/s/photos/zagreb-city",
    "Сплит": "https://unsplash.com/s/photos/split-city",
    "Дубровник": "https://unsplash.com/s/photos/dubrovnik-city",

    "Лисабон": "https://unsplash.com/s/photos/lisbon-city",
    "Порто": "https://unsplash.com/s/photos/porto-city",
    "Фаро": "https://unsplash.com/s/photos/faro-portugal",

    "Варшава": "https://unsplash.com/s/photos/warsaw-city",
    "Краков": "https://unsplash.com/s/photos/krakow-city",
    "Гданск": "https://unsplash.com/s/photos/gdansk-city",

    "Будапеща": "https://unsplash.com/s/photos/budapest-city",
    "Дебрецен": "https://unsplash.com/s/photos/debrecen-city",

    "Цюрих": "https://unsplash.com/s/photos/zurich-city",
    "Женева": "https://unsplash.com/s/photos/geneva-city",
    "Берн": "https://unsplash.com/s/photos/bern-city",

    "Брюксел": "https://unsplash.com/s/photos/brussels-city",
    "Брюж": "https://unsplash.com/s/photos/bruges-city",
    "Антверпен": "https://unsplash.com/s/photos/antwerp-city",

    "Букурещ": "https://unsplash.com/s/photos/bucharest-city",
    "Брашов": "https://unsplash.com/s/photos/brasov-city",
    "Клуж-Напока": "https://unsplash.com/s/photos/cluj-napoca-city",

    "Копенхаген": "https://unsplash.com/s/photos/copenhagen-city",
    "Орхус": "https://unsplash.com/s/photos/aarhus-city",
}




HOTEL_PRICES = {
    "🏠 Бюджетен хотел": 60,
    "🏨 Комфортен хотел": 100,
    "🏰 Луксозен хотел": 170,
}

DISTANCE_BETWEEN_CITIES = 300

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
st.caption("Започни от България и изгради своята идеална европейска почивка")

st.sidebar.header("🧭 Настройки на пътуването")

country = st.sidebar.selectbox(
    "🌐 Избери държава за посещение",
    list(DESTINATIONS.keys())
)

max_cities = len(DESTINATIONS[country])

num_cities = st.sidebar.slider(
    "🏙️ Колко града искаш да посетиш?",
    1,
    max_cities,
    min(3, max_cities)
)

transport_choice = st.sidebar.radio(
    "🚘 Как ще пътуваш?",
    ["Кола", "Влак", "Самолет"]
)

hotel_type = st.sidebar.radio(
    "🛏️ Предпочитан тип настаняване",
    list(HOTEL_PRICES.keys())
)

days = st.sidebar.slider("📆 Продължителност (дни)", 2, 21, 7)
budget = st.sidebar.number_input("💰 Твоят бюджет (лв)", 500, 25000, 4000)

plan = st.sidebar.button("🧭 Планирай пътуването")

# ================== PLANNING ==================

if plan:
    selected_cities = ["София"] + [
        city for city, _ in DESTINATIONS[country][:num_cities]
    ]

    st.subheader("🗺️ Твоят маршрут")
    st.markdown(" ** ➡️ ".join(selected_cities) + "**")

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

    deck = pdk.Deck(
        layers=[
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
                get_radius=900,
                radius_min_pixels=4,
                radius_max_pixels=10,
                get_fill_color=[50, 130, 200],
                pickable=True
            ),
        ],
        initial_view_state=pdk.ViewState(
            latitude=points["lat"].mean(),
            longitude=points["lon"].mean(),
            zoom=4
        )
    )

    st.pydeck_chart(deck)

    # ================== DETAILS ==================

    st.subheader("📍 Градове и преживявания")

    hotel_price = HOTEL_PRICES[hotel_type]
    food_price = 30

    total_food = 0
    total_hotel = 0
    
    for city in selected_cities[1:]:
        food = next(food for c, food in DESTINATIONS[country] if c == city)
    
        with st.expander(city):
            if city in CITY_IMAGES:
                st.image(CITY_IMAGES[city], use_column_width=True)

            st.write(f"🏨 **{hotel_type}:** {hotel_price} лв / нощ")
            st.write(f"🍽️ **Традиционна храна:** {food}")
            st.write("🏛️ **Препоръка:** разходка в историческия център")

        total_food += food_price * days
        total_hotel += hotel_price * days


    # ================== SUMMARY ==================

    transport = Car() if transport_choice == "Кола" else Train() if transport_choice == "Влак" else Plane()

    distance = DISTANCE_BETWEEN_CITIES * (len(selected_cities) - 1)
    total_cost = total_food + total_hotel + transport.travel_cost(distance)

    st.subheader("💰 Обобщение")

    st.write(f"{transport.name()} – {transport.travel_cost(distance):.2f} лв")
    st.write(f"🏨 Настаняване: {total_hotel:.2f} лв")
    st.write(f"🍽️ Храна: {total_food:.2f} лв")

    st.markdown("---")
    st.markdown(f"## 💵 Обща сума: **{total_cost:.2f} лв**")

    if total_cost <= budget:
        st.success("✅ Пътуването е в рамките на бюджета")
    else:
        st.error("❌ Надвишава бюджета")

    st.info(f"🎲 Случайно събитие: {random.choice(['🎉 Фестивал', '🌧️ Дъждовен ден', '💸 Неочаквана отстъпка'])}")
