import streamlit as st
from res.new_syle import page_style
from detectors import load_detector_model, detect
import pandas as pd
import numpy as np
import folium 
from streamlit_folium import st_folium
from geopy.geocoders import Photon
from folium import IFrame
import os
from PIL import Image
from io import BytesIO
import base64
ARHANGELSK_CENTER = (64.5401, 40.5433)

def get_color(true_area, area):
    area = area*0.8
    percentage = (area / true_area) * 100
    color = ('red', 'yellow', 'green')
    predict = ('Большая стихийная свалка', 'Малая стихийная свалка', 'Небольшой объем мусора')
    if percentage >= 0.7: return color[0], predict[0]
    elif 0.7 > percentage >= 0.4: return color[1], predict[1]
    else: return color[2], predict[2]
         
def main():
    page_style()
    img_folder = 'img'
    predict_folder = 'predict_img'
    selector_option = "yolov8n.pt"
    selected_model = load_detector_model(selector_option)
    col1, col2 = st.columns(2)
    with col1:
        st.header("Заполните форму заявки")
        # Виджет для загрузки файла
        uploaded_file = st.file_uploader("Выберите файл", type=["png", "jpg", "jpeg"])
        # Инициализация геолокатора
        geolocator = Photon(user_agent="measurements")
        # Функция для получения подсказок
        def get_suggestions(query):
            try:
                locations = geolocator.geocode(query, exactly_one=False)
                suggestions = [location.address for location in locations]
                return suggestions
            except Exception as e:
                return []
        # Поле для ввода цельного адреса
        if 'text_input_value' not in st.session_state:
            st.session_state['text_input_value'] = ''
        address = st.text_input("Введите адрес - дом, улица, город:", value=st.session_state['text_input_value'], key="address")
        # Кнопка для получения подсказок
        address_suggestions = get_suggestions(address)
        loc_address = st.selectbox("Подсказки по адресу:", address_suggestions, key="address_suggestions")
        location = geolocator.geocode(loc_address)
        latitude, longitude = location.latitude, location.longitude
        if loc_address is not None:
            adr = loc_address
            st.session_state['text_input_value'] = adr
        name = st.text_input("Введите ваше имя:", key="name")
        number = st.text_input("Введите ваш номер телефона:", key="number")
        comment = st.text_input("Кратко опишите проблему:", key="comment")

        def save_data_to_csv(data):
            df = pd.DataFrame([data])
            try:
                df.to_csv('data.csv', mode='a', header=False, index=False)
                return True, "Данные успешно сохранены!"
            except Exception as e:
                return False, f"Ошибка при сохранении данных: {e}"               

        if st.button("Проверить и сохранить"):
            if uploaded_file is not None:
                # Получение имени файла
                file_name = uploaded_file.name
                img_bytes = uploaded_file.getvalue()
                img = Image.open(BytesIO(img_bytes))
                # Сохранение файла в папку img
                file_path = os.path.join(img_folder, file_name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())              
            else:
                st.warning('Пожалуйста, загрузите файл.')      
            predict_crops, area, true_area= detect(selector_option, selected_model, img)
            predict_file_path = os.path.join(predict_folder, file_name)
            predict_crops.save(predict_file_path)
            color, predict_com = get_color(true_area, area)
            data = {
                'photo': file_name,
                'address': adr,
                'name': name,
                'phone_number': number,
                'comment': comment,
                'latitude': latitude,
                'longitude': longitude,
                'color' : color,
                'predict_com' : predict_com,
            }
            save_data_to_csv(data)
            st.success('Заявка успешно загружена')
                
    with col2:
        st.header("Онлайн карта")
        df2 = pd.read_csv('data.csv', encoding='utf-8', sep=',')
        map = folium.Map(location = ARHANGELSK_CENTER, zoom_start = 11)
        for index, row in df2.iterrows():
            latitude = row[5]
            longitude = row[6]
            comment = row[4]
            marker_color = row[7]
            predict_com = row[8]
            img_path = row[0]
            photo_url = f'./{predict_folder}/{img_path}'
            with open(photo_url, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            html_img = f'<img src="data:image/jpeg;base64,{encoded_string}" alt="Фото" style="width:100%; height:auto;">'
            html_text = f'<p style="font-family: Roboto, Arial, sans-serif; font-size: 20px;">Прогноз системы: {predict_com}</p><p style="font-family: Roboto, Arial, sans-serif; font-size: 20px;">Комментарий пользователя: {comment}</p>'
            html_content = html_img + html_text
            iframe = folium.IFrame(html_content, width=400, height=400)
            popup = folium.Popup(iframe, max_width="100%" )
            marker = folium.Marker(location=[latitude, longitude], popup=popup, icon=folium.Icon(color=marker_color))
            map.add_child(marker)
        st_folium(map, width= 650, height = 650)


if __name__ == "__main__":
    main()
