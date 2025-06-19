#import os
#import shutil
#import copy
#import numpy as np
import streamlit as st
#import requests
#import xml.etree.ElementTree as ET
from messages import messages as mess
from dataIO import show_graph
from peaksearch_menu import PeakSearchMenu
from indexing_menu import IndexingMenu

if __name__ == '__main__':
    sel_graph_space = st.empty ()
    
    with st.sidebar:
        #タイトルスペース確保
        title = st.empty()
        
        col1, col2 = st.columns (2)
        #言語選択
        with col1:
            lang_sel = st.radio ('langage', ['English', 'Japanese'],
                             horizontal = True)
            if lang_sel == 'English': lang = 'eng'
            else: lang = 'jpn'
        
        with col2:
            select_menu = st.radio ('menu',
                    [mess[lang]['peaksearch']['main'],
                     mess[lang]['indexing']['main']],
                    horizontal = True)

        #タイトル表記    
        with title:
            st.title (mess[lang]['main_title'])
    
        objPeakSearch = PeakSearchMenu (lang)
        objIndexing = IndexingMenu (lang)

        if select_menu == mess[lang]['peaksearch']['main']:
            out_pk_menu = objPeakSearch.menu()

        else:
            objIndexing.menu()

    #----------------------------------------------------
    #   グラフ表示、ピークサーチ結果表示
    #----------------------------------------------------
    #df, peakDf = out_pk_menu['df'], out_pk_menu['peakDf']
    if 'df' not in st.session_state: df = None
    else: df = st.session_state['df']
    if 'peakDf' not in st.session_state: peakDf = None
    else: peakDf = st.session_state['peakDf']

    mes = mess[lang]['graph']
    options = [mes['diffPattern'], mes['log']]
    
    with sel_graph_space:
        sel_graph = st.radio (
            {'eng' : 'select graph or log',
            'jpn' : 'グラフ・ログ選択'}[lang],
        options = options, horizontal = True,
        key = 'graph_or_log')


    if (df is not None) & (peakDf is not None):
        mes = mess[lang]['graph']
        df.columns = [ 'xphase', 'yphase', 'err_yphase', 'smth_yphase']
                
        graph_area = st.empty()

        dispDf = peakDf
        dispDf.columns = [{'eng' : 'Peak', 'jpn' : 'ピーク'}[lang],
                 mes['pos'], mes['peakH'], mes['fwhm'], mes['sel']]


        st.write (mess[lang]['graph']['result'])
        edited_df = st.data_editor (
            dispDf,
            column_config = {
                mes['sel']: st.column_config.CheckboxColumn(
                            mes['sel'], default = True)},
            use_container_width = True)
        selected = edited_df.loc[edited_df[mes['sel']] == True]
        selected.columns = peakDf.columns



        if select_menu == mess[lang]['peaksearch']['main']:
            with graph_area:
                if sel_graph == mes['diffPattern']:
                    fig = show_graph (df, selected, output = True, lang = lang)
                    st.plotly_chart (fig, use_container_width = True)
                else:
                    objPeakSearch.display_log()
