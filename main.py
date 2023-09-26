import streamlit as st
from open_api import request_open_api
from knowledge_graph import visualize_nodes
import os
import streamlit.components.v1 as components


st.title('知識グラフ')

documents = st.text_input('文章を入力してください')

btnRun = st.button("実行", key=None, help=None, on_click=None, args=None, kwargs=None,)


if btnRun:
    with st.spinner('Processing...'):
        detected_entity = request_open_api(documents)
        visualize_nodes(detected_entity)

        if os.path.exists("edges.html"):
            # st.components.v1.iframe("./edges.html", width=None, height=None, scrolling=False)
            p = open("edges.html")
            components.html(p.read(), height=600)
