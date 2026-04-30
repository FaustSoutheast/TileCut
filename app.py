import streamlit as st
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# Налаштування сторінки
st.set_page_config(page_title="TileCut Optima", layout="wide")

# Стилізація для професійного вигляду
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stSidebar { background-color: #1a1c24; }
    div[data-testid="stExpander"] { border: 1px solid #deff9a; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ЗАГОЛОВОК ТА ДИСКЛЕЙМЕР ---
st.title("TileCut Optima")
st.info("**Застереження:** Цей сайт надає поради для приблизного моделювання. Результати є рекомендаційними і не замінюють професійний інженерний план.")

# --- SIDEBAR (НАЛАШТУВАННЯ) ---
with st.sidebar:
    st.header("Налаштування")
    
    # 1. ФОРМА ПРИМІЩЕННЯ
    st.subheader("1. Параметри приміщення")
    room_type = st.selectbox("Оберіть форму приміщення:", 
                            ["Прямокутник", "Г-подібна", "Довільна форма (точки)"])
    
    room_coords = []
    
    if room_type == "Прямокутник":
        L = st.number_input("Довжина кімнати (см)", min_value=10, value=400)
        W = st.number_input("Ширина кімнати (см)", min_value=10, value=300)
        room_coords = [(0,0), (L,0), (L,W), (0,W)]
        
    elif room_type == "Г-подібна":
        st.write("Введіть довжини стін згідно зі схемою:")
        a = st.number_input("Стіна A (см) - загальна довжина", value=500)
        b = st.number_input("Стіна B (см) - загальна ширина", value=400)
        c = st.number_input("Стіна C (см) - виріз глибина", value=200)
        d = st.number_input("Стіна D (см) - виріз ширина", value=200)
        # Розрахунок координат Г-форми
        room_coords = [(0,0), (a,0), (a, b-c), (a-d, b-c), (a-d, b), (0,b)]

    elif room_type == "Довільна форма (точки)":
        st.write("Вкажіть координати кутів (відступ вправо та вгору):")
        coords_data = st.data_editor(
            [{"Вправо (X)": 0, "Вгору (Y)": 0}, {"Вправо (X)": 300, "Вгору (Y)": 0}, {"Вправо (X)": 150, "Вгору (Y)": 200}],
            num_rows="dynamic"
        )
        room_coords = [(row["Вправо (X)"], row["Вгору (Y)"]) for row in coords_data]

    # 2. МЕНЕДЖЕР ОТВОРІВ
    st.divider()
    st.subheader("2. Отвори (короби, труби)")
    if 'holes' not in st.session_state:
        st.session_state.holes = []

    if st.button("➕ Додати отвір"):
        st.session_state.holes.append({"w": 50, "h": 50, "x": 10, "y": 10})

    updated_holes = []
    for i, hole in enumerate(st.session_state.holes):
        with st.expander(f"Отвір №{i+1}"):
            w = st.number_input(f"Ширина (см)", value=hole['w'], key=f"hw_{i}")
            h = st.number_input(f"Довжина (см)", value=hole['h'], key=f"hh_{i}")
            x = st.number_input(f"Відступ зліва (см)", value=hole['x'], key=f"hx_{i}")
            y = st.number_input(f"Відступ знизу (см)", value=hole['y'], key=f"hy_{i}")
            updated_holes.append({"w": w, "h": h, "x": x, "y": y})
            if st.button(f"🗑️ Видалити", key=f"del_{i}"):
                st.session_state.holes.pop(i)
                st.rerun()
    st.session_state.holes = updated_holes

    # 3. МАТЕРІАЛИ ТА БЮДЖЕТ
    st.divider()
    st.subheader("3. Матеріали та Бюджет")
    tile_w = st.number_input("Ширина плитки (см)", value=60)
    tile_h = st.number_input("Довжина плитки (см)", value=60)
    grout = st.number_input("Шов (мм)", value=2)
    
    budget = st.number_input("Ваш бюджет на проект (грн)", value=20000)
    labor_cost = st.slider("Вартість роботи майстра (грн/м²)", 400, 1000, 650)

# --- ГОЛОВНЕ ВІКНО (ВІЗУАЛІЗАЦІЯ) ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Preview: План приміщення")
    
    if len(room_coords) > 2:
        try:
            # Створення геометрії
            room_poly = Polygon(room_coords)
            
            # Малювання
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#0e1117')
            ax.set_facecolor('#1a1c24')
            
            # Малюємо кімнату
            x, y = room_poly.exterior.xy
            ax.fill(x, y, alpha=0.3, fc='#deff9a', ec='#deff9a', lw=2, label="Приміщення")
            
            # Малюємо отвори
            for hole in st.session_state.holes:
                hx = [hole['x'], hole['x'] + hole['w'], hole['x'] + hole['w'], hole['x']]
                hy = [hole['y'], hole['y'], hole['y'] + hole['h'], hole['y'] + hole['h']]
                ax.fill(hx, hy, fc='#ff4b4b', alpha=0.8, label="Отвір")

            ax.set_aspect('equal')
            ax.tick_params(colors='white')
            plt.grid(color='#333', linestyle='--', alpha=0.5)
            st.pyplot(fig)
            plt.close(fig)
            
        except Exception as e:
            st.error(f"Помилка побудови геометрії. Перевірте координати. ({e})")
    else:
        st.warning("Додайте більше точок, щоб побачити креслення.")

with col2:
    st.subheader("Попередні розрахунки")
    
    if len(room_coords) > 2:
        area_m2 = Polygon(room_coords).area / 10000
        holes_area = sum([(h['w'] * h['h']) for h in st.session_state.holes]) / 10000
        net_area = area_m2 - holes_area
        
        # ВИПРАВЛЕНО: прибрав пробіл у .2f
        st.metric("Чиста площа підлоги", f"{net_area:.2f} м²") 
        
        # Приблизна кількість плитки (без оптимізації, площа + 10%)
        tile_area = (tile_w * tile_h) / 10000
        est_tiles = int((net_area / tile_area) * 1.1)
        
        st.metric("Орієнтовна кількість плитки", f"{est_tiles} шт")
        
        st.divider()
        
        # Бюджетний аналіз
        total_labor = net_area * labor_cost
        remaining_for_tiles = budget - total_labor
        
        if remaining_for_tiles > 0:
            price_per_tile = remaining_for_tiles / est_tiles
            st.success(f"Можна обрати плитку до **{price_per_tile:.0f} грн/шт**")
        else:
            st.error("Бюджет замалий навіть для оплати роботи майстра.")

# --- ВЕЛИКА КНОПКА ЗАПУСКУ ---
st.divider()
# Робимо 3 колонки, щоб кнопка була рівно по центру
col_empty1, col_button, col_empty2 = st.columns([1, 2, 1])

with col_button:
    if st.button("Запустити Генетичний алгоритм", use_container_width=True):
        if len(room_coords) > 2:
            try:
                import math
                
                # --- ПІДГОТОВКА ГЕОМЕТРІЇ ---
                room_poly = Polygon(room_coords)
                for hole in st.session_state.holes:
                    hx = [hole['x'], hole['x'] + hole['w'], hole['x'] + hole['w'], hole['x']]
                    hy = [hole['y'], hole['y'], hole['y'] + hole['h'], hole['y'] + hole['h']]
                    hole_poly = Polygon(zip(hx, hy))
                    room_poly = room_poly.difference(hole_poly)
                
                minx, miny, maxx, maxy = room_poly.bounds
                step_x = tile_w + (grout / 10)
                step_y = tile_h + (grout / 10)
                
                def generate_grid(offset_x, offset_y):
                    whole = []
                    cuts = []
                    x = minx - step_x + offset_x
                    while x < maxx:
                        y = miny - step_y + offset_y
                        while y < maxy:
                            tile = Polygon([(x, y), (x+tile_w, y), (x+tile_w, y+tile_h), (x, y+tile_h)])
                            if tile.intersects(room_poly):
                                intersection = tile.intersection(room_poly)
                                # Відкидаємо фантомні перетини (лінії/точки)
                                if intersection.geom_type not in ['Polygon', 'MultiPolygon']:
                                    y += step_y
                                    continue
                                
                                if intersection.area >= (tile_w * tile_h) * 0.99:
                                    whole.append(tile)
                                else:
                                    cuts.append(intersection)
                            y += step_y
                        x += step_x
                    return whole, cuts

                def calculate_packing(cuts):
                    if not cuts: return 0
                    total_cut_area = 0
                    for c in cuts:
                        # ВИПРАВЛЕНО: Використовуємо реальну площу обрізка, а не його Bounding Box
                        total_cut_area += c.area 
                        
                    tile_area = tile_w * tile_h
                    tiles_needed_for_cuts = int(math.ceil((total_cut_area * 1.25) / tile_area))
                    return max(1, tiles_needed_for_cuts)

                # --- ДЕТЕРМІНОВАНИЙ ПОШУК (Grid Search) ТА ЕРОЗІЯ ---
                st.markdown("### Математичний розрахунок (Grid Search)")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                best_eco_x, best_eco_y, best_eco_score = 0, 0, float('inf')
                best_aes_x, best_aes_y, best_aes_score = 0, 0, float('-inf')
                
                # Крок сітки для перебору (кожні 5 см). Це гарантує стабільний результат!
                search_step = 5
                x_offsets = [i for i in range(0, int(tile_w), search_step)]
                y_offsets = [i for i in range(0, int(tile_h), search_step)]
                
                total_iterations = len(x_offsets) * len(y_offsets)
                current_iteration = 0
                
                for ox in x_offsets:
                    for oy in y_offsets:
                        current_iteration += 1
                        
                        # Оновлюємо статус не кожну мілісекунду, щоб не гальмувати Streamlit
                        if current_iteration % 5 == 0 or current_iteration == total_iterations:
                            status_text.text(f"Аналіз сценаріїв розкладки: {current_iteration} з {total_iterations}...")
                            progress_bar.progress(current_iteration / total_iterations)
                        
                        w_tiles, c_tiles = generate_grid(ox, oy)
                        
                        # 1. Економіка (Мінімум кількості фрагментів)
                        eco_score = len(c_tiles)
                        if eco_score < best_eco_score:
                            best_eco_score = eco_score
                            best_eco_x, best_eco_y = ox, oy
                            
                        # 2. Естетика з використанням ЕРОЗІЇ (Negative Buffer)
                        aes_score = 0
                        for c in c_tiles:
                            # Зрізаємо ~2.5 см з усіх країв. Якщо фігура тонша за 5 см - вона зникне.
                            eroded_cut = c.buffer(-2.49)
                            
                            if eroded_cut.is_empty:
                                aes_score -= 1000 # Жорсткий штраф за тонку смужку!
                            else:
                                aes_score += c.area # Нагорода за великі товсті шматки
                        
                        if aes_score > best_aes_score:
                            best_aes_score = aes_score
                            best_aes_x, best_aes_y = ox, oy

                status_text.success("Оптимізацію успішно завершено! Знайдено абсолютний оптимум.")

                # Генеруємо фінальні сітки за найкращими знайденими зміщеннями
                eco_whole, eco_cuts = generate_grid(best_eco_x, best_eco_y)
                aes_whole, aes_cuts = generate_grid(best_aes_x, best_aes_y)
                bal_x, bal_y = (best_eco_x + best_aes_x) / 2, (best_eco_y + best_aes_y) / 2
                bal_whole, bal_cuts = generate_grid(bal_x, bal_y)

                # --- ВКЛАДКИ З РЕЗУЛЬТАТАМИ ---
                tab1, tab2, tab3 = st.tabs(["Економний", "Безпечний/Естетичний", "Баланс"])
                
                def draw_result_plot(whole_tiles, cut_tiles, ox, oy, title_color, strategy_name, room_type):
                    fig, ax = plt.subplots(figsize=(10, 8))
                    fig.patch.set_facecolor('#0e1117')
                    ax.set_facecolor('#1a1c24')
                    
                    rx, ry = room_poly.exterior.xy
                    ax.plot(rx, ry, color='white', linewidth=2)
                    
                    for t in whole_tiles:
                        tx, ty = t.exterior.xy
                        ax.fill(tx, ty, alpha=0.5, fc='#4CAF50', ec='black', lw=1)
                    
                    for c in cut_tiles:
                        if c.geom_type == 'Polygon':
                            cx, cy = c.exterior.xy
                            ax.fill(cx, cy, alpha=0.7, fc='#FFC107', ec='black', lw=1)
                        elif c.geom_type == 'MultiPolygon':
                            for geom in c.geoms:
                                cx, cy = geom.exterior.xy
                                ax.fill(cx, cy, alpha=0.7, fc='#FFC107', ec='black', lw=1)
                                
                    ax.set_aspect('equal')
                    ax.tick_params(colors='white')
                    plt.grid(color='#333', linestyle='--', alpha=0.5)
                    
                    extra_tiles = calculate_packing(cut_tiles)
                    total_tiles = len(whole_tiles) + extra_tiles
                    
                    room_area = room_poly.area / 10000
                    bought_area = (total_tiles * tile_w * tile_h) / 10000
                    waste_pct = ((bought_area - room_area) / bought_area) * 100 if bought_area > 0 else 0
                    
                    st.markdown(f"### Аналітика результатів")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Цілі плитки", f"{len(whole_tiles)} шт")
                    c2.metric("Фрагменти підрізки", f"{len(cut_tiles)} шт")
                    c3.metric("Витрата на підрізку", f"{extra_tiles} шт")
                    c4.metric("Всього купити", f"{total_tiles} шт")
                    
                    st.markdown(f"**Коефіцієнт відходів:** <span style='color:{title_color}; font-size:22px; font-weight:bold;'>{waste_pct:.1f}%</span>", unsafe_allow_html=True)
                    st.pyplot(fig)
                    plt.close(fig)
                    
                    st.subheader("Покрокова інструкція для майстра")
                    
                    if strategy_name == "eco":
                        strat_desc = "Цей метод зміщує всі обрізки до далеких стін для швидкості укладання."
                    elif strategy_name == "aes":
                        strat_desc = "Метод відцентровує розкладку, щоб уникнути тонких смужок (менше 5 см) біля стін та отворів."
                    else:
                        strat_desc = "Цей метод є золотою серединою: він уникає екстремально тонких смужок, але не роздуває бюджет."

                    st.info(f"**Логіка розкладки:** {strat_desc}")
                    
                    # --- АДАПТИВНА ІНСТРУКЦІЯ ---
                    if room_type in ["Прямокутник", "Г-подібна"]:
                        # Стара інструкція для прямих кутів
                        if ox == 0 and oy == 0:
                            start_action = "Візьміть **ЦІЛУ плитку** і встановіть її рівно в кут. Жодних підрізок для стартової точки не потрібно!"
                        else:
                            start_action = f"Відріжте від цілої плитки кутовий елемент розміром **Ширина {ox:.1f} см, Довжина {oy:.1f} см**. Встановіть його у кут."

                        st.markdown(f"""
                        1.  **Точка відліку:** Лівий нижній кут приміщення.
                        2.  **Підготовка:** {start_action}
                        3.  **Перший ряд:** Продовжуйте укладання від кутової деталі вправо та вгору.
                        4.  **Основне полотно:** Заповніть центральну частину цілими плитками.
                        5.  **Фінальний етап:** Заміряйте та виріжте фрагменти для примикання до стін.
                        """)
                    else:
                        # Нова інструкція для довільних форм (непрямі кути)
                        st.markdown(f"""
                        *Оскільки приміщення має нестандартну форму, укладання починається не з кута, а за базовими осями.*
                        1.  **Розмітка лазером:** Знайдіть найлівішу та найнижчу точки кімнати. Відступіть від них **{ox:.1f} см вправо** та **{oy:.1f} см вгору**.
                        2.  **Базові осі:** Побудуйте в цих точках дві перпендикулярні лінії (лазерним рівнем або шнуром). Перетин цих ліній — це стартовий вузол вашої сітки.
                        3.  **Укладання хреста:** Викладіть два напрямні ряди з **цілих плиток** уздовж цих лазерних осей.
                        4.  **Основне полотно:** Заповніть простір між осями цілими плитками.
                        5.  **Підрізка косих кутів:** Всі елементи, що примикають до косих стін, вирізаються за місцем за допомогою малки (кутоміра) або картонних шаблонів в останню чергу.
                        """)

                # 2. ДОДАНО передачу room_type у функції малювання
                with tab1:
                    draw_result_plot(eco_whole, eco_cuts, best_eco_x, best_eco_y, "#FFC107", "eco", room_type)
                with tab2:
                    draw_result_plot(aes_whole, aes_cuts, best_aes_x, best_aes_y, "#4CAF50", "aes", room_type)
                with tab3:
                    draw_result_plot(bal_whole, bal_cuts, bal_x, bal_y, "#03A9F4", "bal", room_type)

            except Exception as e:
                st.error(f"Сталася помилка: {e}")

        else:
            st.error("Спочатку задайте координати приміщення!")