from gtts import gTTS
import pandas as pd
import streamlit as st
import os
def make_mp3_file(file_name, text, lang):
    if text.strip() == "":
        text = "-"
    if lang == "영어":
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(file_name)
    elif lang == "한국어":
        tts = gTTS(text=text, lang='ko', slow=False)
        tts.save(file_name)
    elif lang == "중국어":
        tts = gTTS(text=text, lang='zh', slow=False)
        tts.save(file_name)

def make_mp3_files_all_languages(file_name):
    df = pd.read_excel(f"./엑셀파일/{file_name}.xlsx", header=None).iloc[:, :3]
    df.columns=["한국어", "영어", "중국어"]
    df.index = df.index + 1

    if not os.path.exists(f"./음성파일/{file_name}"):
        os.mkdir(f"./음성파일/{file_name}")

    for l in ["한국어", "영어", "중국어"]:
        if not os.path.exists(f"./음성파일/{file_name}/{l}"):
            os.mkdir(f"./음성파일/{file_name}/{l}")

    st.write("## MP3 변환 중.. MP3 변환이 완료될 때까지 새로고침을 하지 마세요!")
    my_bar = st.progress(0)
    for row in df.itertuples():
        make_mp3_file(f"./음성파일/{file_name}/한국어/{row[0]}.mp3", row[1], "한국어")
        make_mp3_file(f"./음성파일/{file_name}/영어/{row[0]}.mp3", row[2], "영어")
        make_mp3_file(f"./음성파일/{file_name}/중국어/{row[0]}.mp3", row[3], "중국어")
        # st.write(f"[알림] {row[0]}번째 중국어 문장 음성 변환 완료")
        my_bar.progress(int(row[0] * 100 / df.index[-1]))
    st.success("MP3 변환이 완료되었습니다. 새로고침 해주세요.")