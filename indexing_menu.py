import streamlit as st
from messages import messages as mess

class IndexingMenu:
    def __init__(self,):
        self.mess = mess['eng']

    def menu (self,):
        mes_idx = self.mess['indexing']
        st.write (mes_idx['main'])