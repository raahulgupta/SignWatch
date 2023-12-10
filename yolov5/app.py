import streamlit as st
import torch
from PIL import Image
import os
from gtts import gTTS 
import base64
import glob
from weather import check_rain, load_api_key, get_location, fetch_weather_data


# Load YOLOv5 model
weight_file = 'C:/FV_2.0/Projects/SignWatch_m2/yolov5/runs/train/exp4/weights/best.pt'
model = torch.hub.load('.', 'custom', path=weight_file, source='local', force_reload=True)
model.cpu()

def detect_objects(image):
    results = model(image)
    return results

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

def rain_pred():
    api_key = load_api_key()
    user_location = get_location()
    weather_data = fetch_weather_data(api_key, user_location)
    rainpred = check_rain(weather_data)
    print(rainpred)
    return rainpred

def imageInput(src, lng):
    if src == 'Upload your own data.':
        image_file = st.file_uploader("Upload An Image", type=['png', 'jpeg', 'jpg'])
        col1, col2 = st.columns(2)
        if image_file is not None:
            img = Image.open(image_file)
            with col1:
                st.image(img, caption='Uploaded Image', use_column_width='always')
            imgpath = os.path.join('data/uploads', image_file.name)
            outputpath = os.path.join('data/outputs', os.path.basename(imgpath))
            with open(imgpath, mode="wb") as f:
                f.write(image_file.getbuffer())
            
            # Call Model prediction
            pred = detect_objects(imgpath)

            class_indices = pred.pred[0][:, -1].int().cpu().numpy()
            class_labels = [pred.names[int(idx)] for idx in class_indices]

            pred.render()  # render bbox in image           
            for im in pred.ims:
                im_base64 = Image.fromarray(im)
                im_base64.save(outputpath)

            img_ = Image.open(outputpath)
            with col2:
                st.image(img_, caption='Model Prediction(s)', use_column_width='always')
                text = "There is a: {} ahead".format(", ".join(class_labels))
                tts = gTTS(text, lang=lng)
                tts.save("pred_audio.mp3")
                
                autoplay_audio("pred_audio.mp3")

    elif src == 'From test set.':
        # Image selector slider
        imgpath = glob.glob('data/uploads/*')
        imgsel = st.slider('Select random images from test set.', min_value=1, max_value=len(imgpath), step=1)
        image_file = imgpath[imgsel - 1]
        submit = st.button("Sign Watch!")
        col1, col2 = st.columns(2)
        with col1:
            img = Image.open(image_file)
            st.image(img, caption='Selected Image', use_column_width='always')
        with col2:
            if image_file is not None and submit:
                pred = detect_objects(image_file)  # Use image_file directly for prediction

                class_indices = pred.pred[0][:, -1].int().cpu().numpy()
                class_labels = [pred.names[int(idx)] for idx in class_indices]

                pred.render()  # render bbox in image
                for im in pred.ims:
                    im_base64 = Image.fromarray(im)
                    im_base64.save(os.path.join('data/outputs', os.path.basename(image_file)))

                img_ = Image.open(os.path.join('data/outputs', os.path.basename(image_file)))

                st.image(img_, caption='Model Prediction(s)', use_column_width='always')
                text = "There is a: {} ahead".format(", ".join(class_labels))
                tts = gTTS(text, lang=lng)
                tts.save("pred_audio.mp3")

                autoplay_audio("pred_audio.mp3")
                

def main():
    # Sidebar
    st.sidebar.title('⚙️Options')
    datasrc = st.sidebar.radio("Select input source.", ['From test set.', 'Upload your own data.'])
    lngsrc = st.sidebar.radio("Select language.", ['en', 'fr'])

    st.header('Sign Watch🚦')
    st.subheader('👈🏽 Select the options')
    st.text("")
    st.subheader("Weather Forecast ☔")
    text = rain_pred()
    rain_text = f'{text}'
    tts = gTTS(rain_text, lang=lngsrc)
    tts.save("rain_pred_audio.mp3")
    autoplay_audio("rain_pred_audio.mp3")
    st.text("")
                
    st.sidebar.markdown("https://github.com/Raahul-G?tab=repositories")

    imageInput(datasrc, lngsrc)

if __name__ == '__main__':
    main()
