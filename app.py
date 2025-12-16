import streamlit as st
from abc import ABC, abstractmethod
import pandas as pd
import pydeck as pdk
import time

# ================== DATA ==================
routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"]
}

city_info = {
    "София": {"hotel": "Hotel Sofia Center", "food": "Българска кухня", "sight": "Александър Невски"},
    "Белград": {"hotel": "Belgrade Inn", "food": "Сръбска скара", "sight": "Калемегдан"},
    "Виена": {"hotel": "Vienna City Hotel", "food": "Виенски шницел", "sight": "Шьонбрун"},
    "Мюнхен": {"hotel": "Munich Central", "food": "Немска кухня", "sight": "Мариенплац"}
}

city_coords = {
    "София": [42.6977, 23.3219],
    "Белград": [44.7866, 20.4489],
    "Виена": [48.2082, 16.3738],
    "Мюнхен": [48.1351, 11.5820]
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
st.title("🌍 Туристически планер с анимация и hover")

route_choice = st.selectbox("Маршрут", list(routes.keys()))
transport_choice = st.selectbox("Превоз", ["Кола", "Влак", "Самолет"])
days = st.slider("Брой дни", 1, 10, 4)
budget = st.number_input("Бюджет (лв)", 300, 5000, 1500)

if st.button("🚀 Планирай пътуването"):
    cities = routes[route_choice]
    transport = Car() if transport_choice=="Кола" else Train() if transport_choice=="Влак" else Plane()

    st.subheader("🗺️ Маршрут")
    st.write(" ➡️ ".join(cities))

    # ================== MAP ==================
    points_data = []
    for c in cities:
        info = city_info[c]
        points_data.append({
            "lat": city_coords[c][0],
            "lon": city_coords[c][1],
            "name": c,
            "hotel": info["hotel"],
            "food": info["food"],
            "sight": info["sight"]
        })
    points_df = pd.DataFrame(points_data)

    lines_data = []
    for i in range(len(cities)-1):
        lines_data.append({
            "from_lat": city_coords[cities[i]][0],
            "from_lon": city_coords[cities[i]][1],
            "to_lat": city_coords[cities[i+1]][0],
            "to_lon": city_coords[cities[i+1]][1]
        })
    lines_df = pd.DataFrame(lines_data)

    # Статични точки + линии
    layer_lines = pdk.Layer(
        "LineLayer",
        data=lines_df,
        get_source_position="[from_lon, from_lat]",
        get_target_position="[to_lon, to_lat]",
        get_color=[215,38,61],
        get_width=4
    )

    layer_points = pdk.Layer(
        "ScatterplotLayer",
        data=points_df,
        get_position='[lon, lat]',
        get_radius=1000,
        radius_scale=6,
        get_fill_color=[50,130,200],
        pickable=True,
        tooltip=True
    )

    # ================== ANIMATED ICON ==================
    icon_data = pd.DataFrame([{"lat": city_coords[cities[0]][0], "lon": city_coords[cities[0]][1]}])
    icon_layer = pdk.Layer(
        "ScatterplotLayer",
        data=icon_data,
        get_position='[lon, lat]',
        get_radius=1200,
        get_fill_color=[255, 0, 0],
        radius_min_pixels=6,
        radius_max_pixels=12,
        pickable=False
    )

    view_state = pdk.ViewState(
        latitude=points_df["lat"].mean(),
        longitude=points_df["lon"].mean(),
        zoom=4
    )

    map_placeholder = st.empty()

    # ================== ANIMATION ==================
    num_steps = 30  # брой стъпки между градовете
    for i in range(len(cities)-1):
        start = city_coords[cities[i]]
        end = city_coords[cities[i+1]]
        for step in range(num_steps+1):
            lat = start[0] + (end[0]-start[0])*(step/num_steps)
            lon = start[1] + (end[1]-start[1])*(step/num_steps)
            icon_data = pd.DataFrame([{"lat": lat, "lon": lon}])
            icon_layer.data = icon_data
            map_placeholder.pydeck_chart(pdk.Deck(
                layers=[layer_lines, layer_points, icon_layer],
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/light-v9",
                tooltip={"text":"{name}\n🏨 {hotel}\n🍽️ {food}\n🏛️ {sight}"}
            ))
            time.sleep(0.05)

    # ================== DETAILS ==================
    st.subheader("🏙️ Градове")
    total_food = total_hotel = 0
    for city in cities:
        info = city_info[city]
        with st.expander(f"📍 {city}"):
            st.markdown(f"**🏨 Хотел:** {info['hotel']}")
            st.markdown(f"**🍽️ Храна:** {info['food']}")
            st.markdown(f"**🏛️ Забележителност:** {info['sight']}")
        total_food += days*20
        total_hotel += days*70

    st.subheader("💰 Разходи (приблизителни)")
    st.write(f"Храна: {total_food} лв")
    st.write(f"Хотели: {total_hotel} лв")
    transport_cost = transport.travel_cost(DISTANCE_BETWEEN_CITIES*(len(cities)-1))
    st.write(f"{transport.name()} – транспорт: {transport_cost:.2f} лв")
    st.write(f"Общо: {total_food + total_hotel + transport_cost:.2f} лв")
