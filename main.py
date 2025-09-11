import os
import time
import streamlit as st
from init import setup_session_state
from messages import messages as mess
from dataIO import show_graph, read_inp_xml, read_histo_file,\
    read_inp_xml_conograph, zip_folder, parameter_file_check
from peaksearch_menu import PeakSearchMenu
from indexing_menu import IndexingMenu

if st.session_state['menu_upload'] is None:
    st.session_state['menu_upload'] = False
if st.session_state['menu_peaksearch'] is None:
    st.session_state['menu_peaksearch'] = False
if st.session_state['menu_indexing'] is None:
    st.session_state['menu_indexing'] = False
if st.session_state['uploaded_param'] is None:
    st.session_state['uploaded_param'] = False
if st.session_state['uploaded_hist'] is None:
    st.session_state['uploaded_hist'] = False

class MainMenu:
    def __init__ (self,):
        os.makedirs ('input', exist_ok = True)
        self.param_path = 'input/param.inp.xml'
        self.hist_path = 'input/histogram.txt'
        self.log_peak = 'LOG_PEAKSEARCH.txt'
        self.log_index = 'LOG_CONOGRAPH.txt'
        self.path_sample = 'sample'

    def select_langage (self,):
        lang_sel = st.radio (
            'Select', ['English', 'Japanese'],
                             horizontal = True)
        if lang_sel == 'English': lang = 'eng'
        else: lang = 'jpn'
        st.session_state['lang'] = lang
    
    def select_result_display_menu (self,):
        lang = st.session_state['lang']
        mess_sel = mess[lang]['graph']
        mes_pks = mess_sel['pks_result']
        mes_bestM = mess_sel['bestM']
        mes_lat = mess_sel['latticeConst']
        
        if st.session_state['menu_indexing']:
            menuList = [mes_pks, mes_bestM, mes_lat]
        elif st.session_state['menu_peaksearch']:
            menuList = [mes_pks]
        else : menuList = None

        if menuList is not None:
            sel = st.radio (
                {'eng' : '＜＜Select display menu＞＞',
                'jpn' : '＜＜結果表示の選択＞＞'}[lang],
                menuList, horizontal = True)
    
            return sel
        
        else: return None

    def select_graph_display_menu (self,):
        lang = st.session_state['lang']
        sel_gr_peak = {'eng' : 'Histogram',
                   'jpn' : 'ヒストグラム'}[lang]
        sel_log_1 = {'eng' : 'Log (peak search)',
                   'jpn' : 'ログ (ピークサーチ)'}[lang]
        sel_log_2 = {'eng' : 'Log (indexing)',
                   'jpn' : 'ログ (指標付け)'}[lang]
        
        if st.session_state['menu_indexing']:
            menuList = [sel_gr_peak, sel_log_1, sel_log_2]
        elif st.session_state['menu_peaksearch']:
            menuList = [sel_gr_peak, sel_log_1]
        elif st.session_state['menu_upload']:
            menuList = [sel_gr_peak]
        else:
            menuList = None

        if menuList is not None:
            sel = st.radio (
                {'eng' : '＜＜Display Select Graph or Log＞＞',
                'jpn' : '＜＜グラフ・ログ表示の選択＞＞'}[lang],
                menuList, horizontal = True)
    
            return sel, [sel_gr_peak, sel_log_1, sel_log_2]
        
        else: return None, None
    
    def select_general_menu (self,):
        lang = st.session_state['lang']

        menus = [mess[lang]['peaksearch']['main'],
                 mess[lang]['indexing']['main']]
        
        select_menu = st.radio (
            {'eng' : 'Menu selection',
             'jpn' : 'メニュー選択'}[lang],
             menus, horizontal = True)
        
        return select_menu, menus

    def clear_input_folder (self,):
        if os.path.exists (self.param_path):
            os.remove (self.param_path)
        if os.path.exists (self.hist_path):
            os.remove (self.hist_path)

    def upload_files (self,):
        lang = st.session_state['lang']
        
        param_file = st.file_uploader(
                {'eng' : 'Upload parameter file (xml)',
                'jpn': 'パラメータファイル (xml) アップロード'}[lang],
                type = ['xml'], key = "param")
        
        if st.session_state['param_name'] is not None:
            params = read_inp_xml (self.param_path)
            st.session_state['params'] = params
        
        hist_file = st.file_uploader(
            {'eng' : 'Upload histogram file',
            'jpn': 'ヒストグラムファイル アップロード'}[lang],
            type = ['dat', 'histogramIgor', 'histogramigor', 'txt'],
            key = 'hist')
            
        flg1 = False; flg2 = False
        if param_file:
            with open (self.param_path, 'wb') as f:
                    f.write (param_file.getbuffer ())
            if parameter_file_check (self.param_path):      
                params = read_inp_xml (self.param_path)
                st.session_state ['params'] = params
                st.session_state['default_params'] = params
                params_idx = read_inp_xml_conograph (self.param_path)
                st.session_state['params_idx_defau'] = params_idx
                st.session_state['params_idx'] = params_idx
                flg1 = True
                if (st.session_state['param_name'] is None) or (
                    st.session_state['param_name'] != param_file.name):
                    st.session_state['uploaded_param'] = True
                    st.session_state['param_name'] = param_file.name
            else:
                os.remove (self.param_path)
                st.session_state['param_name'] = None
                st.session_state['params'] = None
                st.session_state['params_idx_defau'] = None
                st.write (
                        {'eng' : '********Please upload correct file..********',
                        'jpn' : '****正しいファイルをアップロードして下さい。****'
                        }[lang])

        if hist_file:
            flg2 = True
            with open (self.hist_path, 'wb') as f:
                    f.write (hist_file.getbuffer ())
            df, _ = read_histo_file (self.hist_path)
            st.session_state['df'] = df
            
            if (st.session_state['hist_name'] is None) or (
                st.session_state['hist_name'] != hist_file.name):
                st.session_state['hist_name'] = hist_file.name
                st.session_state['uploaded_hist'] = True

        if flg1 & flg2:
            st.session_state['menu_upload'] = True

        if st.session_state['uploaded_hist']:
            st.session_state['menu_peaksearch'] = False
            st.session_state['menu_indexing'] = False
            
            st.session_state['peakDf'] = None
            st.session_state['peakDf_selected'] = None
            st.session_state['peakDf_indexing'] = None
            st.session_state['uploaded_hist'] = False

        if (param_file is not None) & (hist_file is not None):
            if os.path.exists (self.log_peak):
                os.remove (self.log_peak)
            if os.path.exists (self.log_index):
                os.remove (self.log_index)

    def down_load_sample (self,):
        lang = st.session_state['lang']
        zip_bytes = zip_folder (self.path_sample)
        st.download_button (
            label = {
                'eng':'Download sample data\n(zip format)', 
                'jpn' : 'サンプルデータ ダウンロード\n(zip形式)'}[lang],
            data = zip_bytes,
            file_name = 'sample.zip')
    
    def downloadParamFile (self,):
        lang = st.session_state['lang']
        with open (self.param_path, 'rb') as f:
            xml_file = f.read()
        
        st.download_button (
                label = {
                    'eng' : 'Down load new parameters',
                    'jpn' : '新しいパラメータのダウンロード'
                    }[lang],
                data = xml_file,
                file_name = self.param_path
            )
        
    def remarks (self,):
        #st.write ('<<< Open side menu!! サイドメニューを開いてください。>>>>')
        st.write ('<<<<Remarks>>>>')
        lang = st.session_state['lang']
        if lang is None: lang = 'eng'
        remarks = {
            'eng' : 'Please note that this web page is provided as a test version and is different from the official CONOGRAPH application available at https://z-code-software.com/.',
            'jpn' : 'このwebページはテスト運用として公開されているページであり、https://z-code-software.com/ にあるCONOGRAPH本体と異なります。'}[lang]
        st.write (remarks)

if __name__ == '__main__':
    #setup_session_state()
    objPeakSearch = PeakSearchMenu ()
    objIndexing = IndexingMenu ()
    objMain = MainMenu ()
    
    remark = st.empty()
    title = st.empty()
    sel_graph_space = st.empty ()
    
    with st.sidebar:
        col1, col2 = st.columns (2)   
        with col1: objMain.select_langage ()
        lang = st.session_state['lang']
        with remark: objMain.remarks()
        objPeakSearch.set_language ()
        objIndexing.set_language ()

        with col2: objMain.down_load_sample ()
        with st.container (border = True):
            objMain.upload_files ()


        #タイトル表記    
        with title:
            st.title (mess[lang]['main_title'])

        if st.session_state['menu_upload']:
            out_pk_menu = objPeakSearch.menu()
        
        if st.session_state['menu_peaksearch']:
            objIndexing.menu()

    #----------------------------------------------------
    #   グラフ表示、ピークサーチ結果表示
    #----------------------------------------------------
    df = st.session_state['df']
    peakDf = st.session_state['peakDf']

    mes = mess[lang]['graph']

    if st.session_state['menu_upload'
            ] | st.session_state['menu_peaksearch'
                ] | st.session_state['menu_indexing']:
        
        with st.container (border = True):
            sel_gr, sels_gr = objMain.select_graph_display_menu ()
            graph_log_area = st.empty()
        
        with st.container (border = True):
            menu_disp = objMain.select_result_display_menu()
        #assert menu_disp is not None
            if menu_disp == mes['pks_result']:
                if peakDf is not None:
                    selected = objPeakSearch.edit_table_peak(peakDf)
                    st.session_state['peakDf_selected'] = selected
                    objPeakSearch.feedbackSelectedPeakToFile (selected)
            elif menu_disp == mes['bestM']:
                objIndexing.disp_bestM ()
            elif menu_disp == mes['latticeConst']:
                objIndexing.menu_select_candidate ()
                objIndexing.operation_summary ()

        with graph_log_area:
            if sel_gr == sels_gr[0]:
                selected = st.session_state['peakDf_selected']
                peakDf_indexing = st.session_state['peakDf_indexing']
                fig = show_graph (df, selected, peakDf_indexing, lang = lang)
                st.plotly_chart (fig, use_container_width = True)
            
            elif sel_gr == sels_gr[1]:
                log = objPeakSearch.request_log()
                objPeakSearch.display_log ()

            else:
                log = objIndexing.request_log()
                objIndexing.display_log()
