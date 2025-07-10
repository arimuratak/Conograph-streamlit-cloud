import streamlit as st
from init import setup_session_state
from messages import messages as mess
from dataIO import show_graph
from peaksearch_menu import PeakSearchMenu
#from indexing_menu import IndexingMenu

if __name__ == '__main__':
    setup_session_state()
    objPeakSearch = PeakSearchMenu ()
    #objIndexing = IndexingMenu ()
    
    st.write ('<<< Open side menu!! サイドメニューを開いてください。>>>>')
    st.write ('<<<<Remarks>>>>')
    st.write ('Please note that this web page is provided as a test version and is different from the official CONOGRAPH application available at https://z-code-software.com/.')
    st.write ('このwebページはテスト運用として公開されているページであり、https://z-code-software.com/ にあるCONOGRAPH本体と異なります。')
    
    title = st.empty()

    sel_graph_space = st.empty ()
    
    with st.sidebar:        
        col1, col2 = st.columns (2)
        #言語選択
        with col1:
            lang_sel = st.radio ('langage', ['English', 'Japanese'],
                             horizontal = True)
            if lang_sel == 'English': lang = 'eng'
            else: lang = 'jpn'
            st.session_state['lang'] = lang
            objPeakSearch.set_language ()
            #objIndexing.set_language ()

        with col2:
            select_menu = st.radio ('menu',
                    [mess[lang]['peaksearch']['main'],
                     mess[lang]['indexing']['main']],
                    horizontal = True)

        #タイトル表記    
        with title:
            st.title (mess[lang]['main_title'])
    
        if select_menu == mess[lang]['peaksearch']['main']:
            out_pk_menu = objPeakSearch.menu()

        else:
            st.write ('Under develoment...')
            #objIndexing.menu()

    #----------------------------------------------------
    #   グラフ表示、ピークサーチ結果表示
    #----------------------------------------------------
    df = st.session_state['df']
    peakDf = st.session_state['peakDf']

    mes = mess[lang]['graph']
    options = [mes['diffPattern'], mes['log']]

    if (df is not None) & (peakDf is not None):
        if select_menu == mess[lang]['peaksearch']['main']:
            with sel_graph_space:
                sel_graph = st.radio (
                        {'eng' : 'select graph or log',
                        'jpn' : 'グラフ・ログ選択'}[lang],
                        options = options, horizontal = True,
                key = 'graph_or_log')

            graph_log_area = st.empty()
            selected = objPeakSearch.edit_table_peak(peakDf)

            with graph_log_area:
                if sel_graph == mes['diffPattern']:
                    fig = show_graph (df, selected, lang = lang)
                    st.plotly_chart (fig, use_container_width = True)
                else:
                    objPeakSearch.display_log()
