from unicodedata import normalize
import glob
import json
import os
import shutil
import time
import streamlit as st
import pandas as pd
import base64
from pydub import AudioSegment
import streamlit.components.v1 as components
import TTS_Module
from streamlit_javascript import st_javascript


def client_ip():
    url = 'https://api.ipify.org?format=json'
    script = (f'await fetch("{url}").then('
                'function(response) {'
                    'return response.json();'
                '})')
    try:
        result = st_javascript(script)

        if isinstance(result, dict) and 'ip' in result:
            return result['ip']
    except:
        return ""

def get_audio_length(file_name):
    audio = AudioSegment.from_file(file_name)
    return audio.duration_seconds

def audio_autoplay(file_name, play_speed, repeat_num):

    mymidia_placeholder = st.empty()
    audio_file = open(file_name, 'rb')
    audio_bytes = audio_file.read()

    mymidia_str = f"data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}"
    mymidia_html = f"""
    <audio autoplay id="stAudio">
    <source src="{mymidia_str}" type="audio/mp3">
    Your browser does not support the audio element.
    </audio>
    <script type="text/javascript"> 
    var audio = document.getElementById("stAudio"); 
    audio.playbackRate={play_speed};
    
    var loops = {repeat_num};       
    var count = 1;
    audio.onended = function() {{
        if(count < loops){{
            count++;
            this.play();
        }}
        else {{
            var temp_elem = document.getElementById("stAudio");
            temp_elem.className = "end"
        }}  
    }};
    
    </script>
    """
    with mymidia_placeholder:
        components.html(mymidia_html)
        time.sleep(1+(get_audio_length(file_name)/play_speed) * repeat_num)

    mymidia_placeholder.empty()

def setting_lang(lang):
    check = False
    interval_time = 0
    sound_repeat_num = 0
    sound_check = True
    sound_speed = 1.0

    get_saved_data = {}
    for i in setting_dict["언어설정"]:
        if i["언어"] == lang:
            get_saved_data = i
            break

    check = st.checkbox(f"{lang} 자막", key=lang, value=get_saved_data["자막"] if get_saved_data else False)
    with st.expander(f"{lang} 설정"):
        interval_time = st.slider("간격 (초)", 0.0, 5.0, step=0.1, key=lang, value=float(get_saved_data["간격"]) if get_saved_data else 0.1)
        sound = st.checkbox("소리", key=lang, value=get_saved_data["소리"] if get_saved_data else False)
        if sound:
            sound_speed = st.slider("배속", 1.0, 6.0, step=0.1, key=lang, value=float(get_saved_data["배속"]) if get_saved_data else 1.0)
            sound_repeat_num = st.slider("반복 횟수", 1, 5, step=1, key=lang, value=int(get_saved_data["반복횟수"]) if get_saved_data else 1)
    result = {"언어":lang, "자막":check, "간격":interval_time, "소리":sound, "배속":sound_speed, "반복횟수":sound_repeat_num}
    return result

def save_uploaded_file(uploadedfile):
    if uploadedfile.name in list(map(os.path.basename, glob.glob("./엑셀파일/*.xlsx"))):
        st.error("동일한 파일 이름이 존재합니다. 파일 이름을 변경하거나 다른 파일을 업로드해주세요.")
    else:
        with open(os.path.join("./엑셀파일",uploadedfile.name),"wb") as f:
            f.write(uploadedfile.getbuffer())
            st.success("업로드 완료하였습니다. MP3 변환을 시작합니다.".format(uploadedfile.name))
            TTS_Module.make_mp3_files_all_languages(uploadedfile.name.replace(".xlsx", ""))


ip_address = client_ip()
f_setting = open("./lang_setting.txt", "r", encoding="utf-8")
f_setting_dict = json.loads(f_setting.read())
if ip_address:
    setting_dict = f_setting_dict[ip_address]
elif (ip_address == "") or (ip_address not in list(f_setting_dict.keys())):
    setting_dict = {
"엑셀파일": "600new.xlsx",
"시작번호": 1,
"끝번호": 600,
"자막크기": 1,
"언어설정": [{"언어": "한국어", "자막": True, "간격": 0.0, "소리": True, "배속": 1.0, "반복횟수": 1}, {"언어": "영어", "자막": True, "간격": 0.0, "소리": True, "배속": 1.0, "반복횟수": 1}, {"언어": "중국어", "자막": True, "간격": 0.0, "소리": True, "배속": 1.0, "반복횟수": 1}],
"자막순서": ["한국어", "영어", "중국어"] }

def nfd2nfc(data):
    return normalize("NFC", data)

with st.sidebar:
    start_button_1 = st.sidebar.button("시작", key="button1")
    st.write("---")
    excel_file_list = list(map(os.path.basename, glob.glob("./엑셀파일/*.xlsx")))
    excel_file_list = list(map(nfd2nfc, excel_file_list))

    if setting_dict["엑셀파일"] not in excel_file_list:
        setting_dict["엑셀파일"] = excel_file_list[0]

    selected_file_name = st.radio(
        "사용할 엑셀 파일",
        excel_file_list, index=excel_file_list.index(setting_dict["엑셀파일"])
    )

    with st.expander("새로운 엑셀 파일 업로드"):
        datafile = st.file_uploader("엑셀 업로드", type=['xlsx'])
        if datafile is not None:
            save_uploaded_file(datafile)
    with st.expander("기존 파일 삭제"):
        remove_file_name = st.radio(
            "삭제할 엑셀 파일 선택",
            list(map(os.path.basename, glob.glob("./엑셀파일/*.xlsx")))
        )
        remove_ok = st.button("삭제")
        if remove_ok:
            os.remove(f"./엑셀파일/{remove_file_name}")
            shutil.rmtree(f"./음성파일/{remove_file_name.replace('.xlsx', '')}")
            st.success("파일 삭제 완료! 새로 고침 해주세요.")
    st.write("---")



    df = pd.read_excel(f"./엑셀파일/{selected_file_name}", header=None).iloc[:, :3]
    df.columns = ["한국어", "영어", "중국어"]
    df.index = df.index + 1

    # take_range = st.slider("구간", min_value=1, max_value=df.index[-1], value=(1, df.index[-1]))
    take_range = [0, 0]
    start_value = setting_dict["시작번호"] if not df.index[-1] < setting_dict["시작번호"] else 1
    end_value = setting_dict["끝번호"] if not df.index[-1] < setting_dict["끝번호"] else df.index[-1]
    take_range[0] = st.number_input('(구간) 시작번호 선택', min_value=1, max_value=df.index[-1], value=start_value, step=1)
    take_range[1] = st.number_input('(구간) 끝번호 선택', min_value=1, max_value=df.index[-1], value=end_value, step=1)
    text_scale = st.slider("자막 크기 설정", 1, 6, step=1, value=setting_dict["자막크기"])


    lang_list = ["한국어", "영어", "중국어"]
    setting_list = []
    for lang in lang_list:
        setting_result = setting_lang(lang)
        if setting_result["자막"]:
            setting_list.append(setting_result)

    selected_language = [l["언어"] for l in setting_list]

    st.write("## 자막 순서 설정")

    language_order = []
    if sorted(selected_language) == sorted(setting_dict["자막순서"]):
        for lan in selected_language:
            language_order.append(st.selectbox(f"{selected_language.index(lan) + 1}번째",
                                               [l for l in setting_dict["자막순서"] if l not in language_order]))
    else:
        for lan in selected_language:
            language_order.append(st.selectbox(f"{selected_language.index(lan) + 1}번째",
                                               [l for l in selected_language if l not in language_order]))

    temp = []
    for lan in language_order:
        for setting_list_item in setting_list:
            if setting_list_item["언어"] == lan:
                temp.append(setting_list_item)
                break
    setting_list = temp

    start_button_2 = st.sidebar.button("시작", key="button2")

if start_button_1 or start_button_2:

    setting_json_to_save = { ip_address :{
        "엑셀파일" : selected_file_name,
        "시작번호" : take_range[0],
        "끝번호" : take_range[1],
        "자막크기" : text_scale,
        "언어설정" : setting_list,
        "자막순서" : language_order
    }
    }

    with open("./lang_setting.txt", "w", encoding="UTF-8") as f:
        f.write(json.dumps(setting_json_to_save, ensure_ascii=False))

    print(setting_json_to_save)

    time.sleep(4)
    df = df.iloc[take_range[0]-1:take_range[1], :]

    if not setting_list:
        st.write("자막 언어를 설정해주세요!")
    else:
        df = df[[i["언어"] for i in setting_list]]


    lang_info = [f"{i['언어']} {i['배속']} 배속" for i in setting_list]
    lang_info = " / ".join(lang_info)

    for i in df.itertuples():
        placeholder_list = [st.empty() for _ in range(len(setting_list) + 1)]
        placeholder_list[0].write("#" * (7-text_scale) + " " + f"{i[0]}번 ({lang_info})")
        num = 1
        for j in i[1:]:
            placeholder_list[num].write("#" * (7-text_scale) + " " + j)
            if setting_list[num-1]["배속"] != 0:
                audio_autoplay(f"./음성파일/{selected_file_name.replace('.xlsx', '')}/{setting_list[num-1]['언어']}/{i[0]}.mp3", play_speed=setting_list[num-1]["배속"], repeat_num=setting_list[num-1]["반복횟수"])

            time.sleep(setting_list[num-1]["간격"])
            num += 1
        for k in range(len(setting_list)+1):
            placeholder_list[k].empty()