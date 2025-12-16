import streamlit as st

from abc import ABC, abstractmethod



# ================== DATA ==================



routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"],
    "България → Италия": ["София", "Скопие", "Рим", "Флоренция"],
    "България → Франция": ["София", "Будапеща", "Прага", "Париж"],
    "Балканска обиколка": ["София", "Скопие", "Тирана", "Дубровник"]
}




city_info({

    "Скопие": {
        "hotel": ("Skopje Square Hotel", 60),
        "food": ("Македонска кухня", 18),
        "sight": "Каменният мост"
    },

    "Рим": {
        "hotel": ("Hotel Roma Centrale", 110),
        "food": ("Италианска паста", 35),
        "sight": "Колизеумът"
    },

    "Флоренция": {
        "hotel": ("Florence Art Hotel", 95),
        "food": ("Тосканска кухня", 32),
        "sight": "Катедралата Санта Мария дел Фиоре"
    },

    "Будапеща": {
        "hotel": ("Danube View Hotel", 85),
        "food": ("Унгарски гулаш", 25),
        "sight": "Парламентът на Унгария"
    },

    "Прага": {
        "hotel": ("Old Town Prague Hotel", 80),
        "food": ("Чешка кухня", 24),
        "sight": "Карловият мост"
    },

    "Париж": {
        "hotel": ("Paris Central Boutique", 120),
        "food": ("Френска кухня", 40),
        "sight": "Айфеловата кула"
    },

    "Тирана": {
        "hotel": ("Tirana City Hotel", 55),
        "food": ("Албанска кухня", 17),
        "sight": "Площад Скандербег"
    },

    "Дубровник": {
        "hotel": ("Adriatic View Hotel", 100),
        "food": ("Средиземноморска кухня", 30),
        "sight": "Старият град на Дубровник"
    }

})




DISTANCE_BETWEEN_CITIES = 300 # км (опростено)



# ================== OOP ==================



class Transport(ABC):

  def __init__(self, price_per_km):

    self.price_per_km = price_per_km



  @abstractmethod

  def name(self):

    pass



  def travel_cost(self, distance):

    return distance * self.price_per_km





class Car(Transport):

  def __init__(self):

    super().__init__(0.25)



  def name(self):

    return "🚗 Кола"





class Train(Transport):

  def __init__(self):

    super().__init__(0.18)



  def name(self):

    return "🚆 Влак"





class Plane(Transport):

  def __init__(self):

    super().__init__(0.45)



  def name(self):

    return "✈️ Самолет"





# ================== UI ==================



st.title("🌍 Интерактивен туристически планер")



route_choice = st.selectbox(

  "Избери маршрут:",

  list(routes.keys())

)



transport_choice = st.selectbox(

  "Превозно средство:",

  ["Кола", "Влак", "Самолет"]

)



days = st.slider("Брой дни за пътуването:", 1, 10, 4)

budget = st.number_input("Твоят бюджет (лв):", 300, 5000, 1500)



if st.button("Планирай пътуването 🧭"):

  cities = routes[route_choice]



  # Избор на транспорт (полиморфизъм)

  if transport_choice == "Кола":

    transport = Car()

  elif transport_choice == "Влак":

    transport = Train()

  else:

    transport = Plane()



  st.subheader("🗺️ Маршрут")

  st.write(" ➡️ ".join(cities))



  # ================== CITY DETAILS ==================

  st.subheader("🏙️ Спирки и предложения")



  total_food_cost = 0

  total_hotel_cost = 0



  for city in cities:

    info = city_info[city]



    st.markdown(f"### 📍 {city}")

    st.write(f"🏨 **Хотел:** {info['hotel'][0]} – {info['hotel'][1]} лв/нощ")

    st.write(f"🍽️ **Храна:** {info['food'][0]} – {info['food'][1]} лв/ден")

    st.write(f"🏛️ **Забележителност:** {info['sight']}")



    total_food_cost += info['food'][1] * days

    total_hotel_cost += info['hotel'][1] * days



  # ================== COST CALCULATION ==================

  total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)

  transport_cost = transport.travel_cost(total_distance)



  total_cost = transport_cost + total_food_cost + total_hotel_cost



  # ================== RESULTS ==================

  st.subheader("💰 Разходи")

  st.write(f"{transport.name()} – транспорт: {transport_cost:.2f} лв")

  st.write(f"🍽️ Храна: {total_food_cost:.2f} лв")

  st.write(f"🏨 Хотели: {total_hotel_cost:.2f} лв")



  st.markdown("---")

  st.write(f"## 💵 Общ бюджет: **{total_cost:.2f} лв**")



  if total_cost <= budget:

    st.success("✅ Бюджетът е достатъчен! Приятно пътуване ✨")

  else:

    st.error("❌ Бюджетът не достига. Помисли за по-евтин транспорт или по-малко дни.")
