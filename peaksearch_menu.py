import os
#import shutil
#import copy
import numpy as np
import streamlit as st
import requests
#import xml.etree.ElementTree as ET
from messages import messages as mess
from dataIO import read_inp_xml, change_inp_xml, zip_folder,\
                    read_output_file

class PeakSearchMenu:
    def __init__ (self, ):
        self.api_url = 'https://conograph-api-server.onrender.com'
        #self.api_url = "http://localhost:8000"
        
        self.setup_session_state ()

        self.pathSample = 'sample'
        self.mess = None #mess[lang]['peaksearch']
        self.mess_gr = None #mess[lang]['graph']
        self.param_name = None
        self.hist_name = None
        self.param_path = 'param.imp.xml'
        self.hist_path = 'histogram.txt'
        self.out_path = 'output.txt'
        self.params = None
        
        self.hist_file = None
        self.log_path = 'LOG_PEAKSEARCH.txt'
        
    def setup_session_state (self,):
        if 'lang' not in st.session_state:
            st.session_state['lang'] = None
        if 'mess_pk' not in st.session_state:
            st.session_state['mess_pk'] = None
        if 'mess_gr' not in st.session_state:
            st.session_state['mess_gr'] = None
        if 'param_name' not in st.session_state:
            st.session_state['param_name'] = None
        if 'hist_name' not in st.session_state:
            st.session_state['hist_name'] = None
        if 'default_params' not in st.session_state:
            st.session_state['default_params'] = None
        if 'params' not in st.session_state:
            st.session_state['params'] = None
        if 'uploaded_map' not in st.session_state:
            st.session_state['uploaded_map'] = None
        if 'df' not in st.session_state:
            st.session_state['df'] = None
        if 'peakDf' not in st.session_state:
            st.session_state['peakDf'] = None


    def set_language (self, lang):
        st.session_state['lang'] = lang
        st.session_state['mess_pk'] = mess[lang]['peaksearch']
        st.session_state['mess_gr'] = mess[lang]['graph']
        
    def down_load_sample (self,):
        lang = st.session_state['lang']
        zip_bytes = zip_folder (self.pathSample)
        st.download_button (
            label = {
                'eng':'Download sample data (zip format)', 
                'jpn' : 'サンプルデータ ダウンロード (zip形式)'}[lang],
            data = zip_bytes,
            file_name = 'sample.zip')

    def display_log (self,):
        with open (self.log_path, 'r', encoding = 'utf-8') as f:
            text = f.read()
        st.text_area ('log', text, height = 400)

    #------------------------------------------------
    #   upload parameter & histogram file &
    #   save as binary format
    #------------------------------------------------
    def upload_files (self,):
        lang = st.session_state['lang']
        param_file = st.file_uploader(
                            {'eng' : 'Upload parameter file (xml)',
                            'jpn': 'パラメータファイル (xml) アップロード'}[lang],
                            type = ["xml"], key = "param")
        if st.session_state['param_name'] is not None:
            name = st.session_state['param_name']
            st.write (
                {'eng' : 'File {} is saved.'.format (name),
                 'jpn' : 'ファイル {} が保存されています。'.format(name)
                 }[lang])
            self.params = read_inp_xml (self.param_path)
            st.session_state['params'] = self.params
        
        hist_file = st.file_uploader(
                            {'eng' : 'Upload histogram file',
                            'jpn': 'ヒストグラムファイル アップロード'}[lang],
                            type = ["dat", "histogramIgor", "histogramigor"], key = "hist")
        if st.session_state['hist_name'] is not None:
            name = st.session_state['hist_name']
            st.write (
                {'eng' : 'File {} is saved.'.format (name),
                 'jpn' : 'ファイル {} が保存されています。'.format(name)
                 }[lang]
            )

        if param_file:
            st.session_state['param_name'] = param_file.name
            #self.param_name = param_file.name
            with open (self.param_path, 'wb') as f:
                f.write (param_file.getbuffer ())
            params = read_inp_xml (self.param_path)
            st.session_state ['params'] = params
            st.session_state['default_params'] = params

        if hist_file:
            st.session_state['hist_name'] = hist_file.name
            #self.hist_name = hist_file.name
            with open (self.hist_path, 'wb') as f:
                f.write (hist_file.getbuffer ())

    def load_files (self,):
        param_name = st.session_state['param_name']
        hist_name = st.session_state['hist_name']
        uploaded_map = {}
        with open (self.param_path, 'rb') as f:
            uploaded_map[param_name] = f.read()
        with open (self.hist_path, 'rb') as f:
            uploaded_map[hist_name] = f.read ()
        #st.session_state['uploaded_map'] = uploaded_map
        return uploaded_map

    def display_param (self, params):
        lang = st.session_state['lang']
        if st.toggle (
            {'eng' : 'Show Default Parameter',
            'jpn' : 'パラメータ初期値 表示'}[lang]):
            text = self.params2text (params)
            st.write (text)

    def exec_peaksearch (self, uploaded_map):
        lang = st.session_state['lang']
        if st.button ({'eng' : 'Exec','jpn':'実行'}[lang]):
            files = {}
            for fname, fobj in uploaded_map.items():
                files[fname] = (fname, fobj,
                                'application/octet-stream')
            
            res = requests.post (
                self.api_url + '/run_cpp', files = files)
            return res
        return None

    def request_log (self,):
        res = requests.post (
            self.api_url + '/log_file')
        
        if res is None: ans = None
        else:
            if res.status_code == 200:
                if os.path.exists (self.log_path):
                    os.remove (self.log_path)
                content = res.content.decode ('utf-8')
                with open (self.log_path, 'w', encoding = 'utf-8') as f:
                    f.write (content)
                ans = self.log_path
            else:
                ans = 'Error 500'

        return ans

    def edit_table_peak (self, peakDf):
        lang = st.session_state['lang']
        mess_gr = st.session_state['mess_gr']
        dispDf = peakDf
        dispDf.columns = [
            {'eng' : 'Peak', 'jpn' : 'ピーク'}[lang],
                mess_gr['pos'], mess_gr['peakH'],
                mess_gr['fwhm'], mess_gr['sel']]

        st.write (mess_gr['result'])
        edited_df = st.data_editor (
            dispDf,
            column_config = {
                mess_gr['sel']: st.column_config.CheckboxColumn(
                            mess_gr['sel'], default = True)},
            use_container_width = True)
        selected = edited_df.loc[edited_df[mess_gr['sel']] == True]
        selected.columns = peakDf.columns
        return selected

    def smthParams (self, params):
        mess_pk = st.session_state['mess_pk']
        st.write (mess_pk['smth_mes'])
        col1,col2 = st.columns (2)
        nPointsDefault = params['nPoints']
        endRegionDefault = params['endRegion'] 
        with col1:
            nPoints = st.text_input (
                mess_pk['tbl_col1'],
                nPointsDefault)
        with col2:
            endRegion = st.text_input (
                mess_pk['tbl_col2'],
                endRegionDefault)
            
        return nPoints, endRegion
    
    def rangeParam (self, params):
        mess_pk = st.session_state['mess_pk']
        st.write (mess_pk['area_mes'])
        col1,col2 = st.columns (2)
        rangeMin, rangeMax = params['minRange'], params['maxRange']
        if rangeMin == 'MIN': rangeMin = 0.0
        with col1:
            minRange = st.text_input ('min', rangeMin)
        with col2:
            maxRange = st.text_input ('max', rangeMax)

        return minRange, maxRange
    
    def thresholdParam (self, params):
        mess_pk = st.session_state['mess_pk']
        lang = st.session_state['lang']
        st.write (mess_pk['th_mes'])
        col1, col2 = st.columns ([2,8])
        c_def = params['c_fixed']
        useErrDict = {
            1 : mess_pk['th_sel_1'],
            0 : mess_pk['th_sel_2']}
        
        with col1:
            c_fixed = st.text_input ('c : ', c_def)
        
        with col2:
            use_error = st.selectbox (
                {'eng' : 'select','jpn' : '選択'}[lang],
                options = list (useErrDict.values()))

        return c_fixed, use_error

    def kalpha2Select (self,):
        mess_pk = st.session_state['mess_pk']
        yes = mess_pk['exec_sel_1']
        no = mess_pk['exec_sel_2']
        select = st.radio (mess_pk['delpk_mes'],
                           [yes, no], horizontal = True)
        return select

    def kaplha2Param (self, params):
        mess_pk = st.session_state['mess_pk']
        mat = np.array ([
            [0.5594075, 0.563798],
            [0.709300, 0.713590],
            [1.540562, 1.544398],
            [1.788965, 1.792850],
            [1.936042, 1.939980],
            [2.289700, 2.293606]])
        kalpha1, kalpha2 = params['kalpha1'], params['kalpha2']
        kalphas = np.array ([[kalpha1, kalpha2]])
        dist = np.sqrt (np.power (mat - kalphas, 2).sum(axis = 1))
        idx = np.argmin (dist)

        params = [
            'Ag / 0.5594075 / 0.563798',
            'Mo / 0.709300 / 0.713590',
            'Cu / 1.540562 / 1.544398',
            'Co / 1.788965 / 1.792850',
            'Fe / 1.936042 / 1.939980',
            'Cr / 2.289700 / 2.293606']
        
        sel = st.selectbox (
            mess_pk['wavelen_mes'],
            params, index = int (idx))
        
        kalpha1, kalpha2 = sel.split (' / ')[1:]
        #st.write (kalpha1, kalpha2)
        return kalpha1, kalpha2


    def operationParam (self, params, savePath):
        defParams = st.session_state['params']
        mess_pk = st.session_state['mess_pk']
        #nPoins = params['nPoints']; endRegion = params['endRegion']
        minRange = params['minRange'] #; maxRange = params['maxRange']
        #c_fixed = params['c_fixed'];
        useErr = params['useErr']
        select = params['select']
        kalpha1 = params['kalpha1']; kalpha2 = params['kalpha2']
        if str (minRange) == '0.0': params['minRange'] = 'MIN'
        params['useErr'] = int (useErr == mess_pk['th_sel_1'])
        params['select'] = int (select == mess_pk['exec_sel_1'])
        if (kalpha1 == None) | (kalpha2 == None):
            params['kalpha1'] = defParams['kalpha1']
            params['kalpha2'] = defParams['kalpha2']
        change_inp_xml (params, savePath)

    def params2text (self, params):
        lang = st.session_state['lang']
        mess_pk = st.session_state['mess_pk']
        text = ''
        nPoints = params['nPoints']
        endRegion = params['endRegion']
        range_begin, range_end = params['minRange'], params['maxRange']
        threshold, useErr = params['c_fixed'], params['useErr']
        alpha2_correction = params['select']
        kalpha1, kalpha2 = params['kalpha1'], params['kalpha2']

        text += {'eng':'Smoothing / ', 'jpn' : '平滑化 / '}[lang]
        text += mess_pk['tbl_col1'] + ' : {}, '.format (nPoints)
        text += mess_pk['tbl_col2'] + ' : {}  \n'.format (endRegion)

        text += mess_pk['area_mes'] + ' / '
        text += 'min : {}, max : {}  \n'.format (range_begin, range_end)
        text += {'eng':'threshold', 'jpn' : 'しきい値'}[lang] + ' / '
        text += 'c : {}, '.format (threshold)
        text += {0 : mess_pk['th_sel_2'],
                 1 : mess_pk['th_sel_1']
                 }[int (useErr)] + '  \n'

        text += mess_pk['delpk_mes'] + ' / '
        text += {0 : mess_pk['exec_sel_2'],
                 1 : mess_pk['exec_sel_1']
                 }[int (alpha2_correction)] + '  \n'
        
        text += 'kα1 : {}, kα2 : {}'.format (kalpha1, kalpha2)
        return text

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
                file_name = 'param.imp.xml'
            )

    def get_result (self, res):
        if res is None:
            ans = None
        else:
            if res.status_code == 200:
                if os.path.exists (self.out_path):
                    os.remove (self.out_path)
                with open (self.out_path, 'wb') as f:
                    f.write (res.content)
                ans = read_output_file (self.out_path)
            elif res.status_code == 500:
                ans = 'Error 500'
        return ans
    
    def reset_files (self,):
        if os.path.exists (self.param_path): os.remove (self.param_path)
        if os.path.exists (self.hist_path): os.remove (self.hist_path)

    def menu (self,):
        mess_pk = st.session_state['mess_pk']
        #self.reset_files ()
        ans = {k : None for k in [
            'defaultParam', 'df', 'peakDf', 'nPoints', 'endRegion',
            'minRange, maxRange, c_fixed', 'useErr','select',
            'kalpha1', 'kalpha2', 'folder', 'log']}

        self.down_load_sample ()
        self.upload_files ()

        if st.session_state['params'] is not None:
            default_params = st.session_state['default_params']
            params = st.session_state['params']
            self.display_param (default_params)

            ans['nPoints'], ans['endRegion'] = \
                            self.smthParams (params)
            ans['minRange'], ans['maxRange'] = \
                            self.rangeParam (params)
            ans['c_fixed'],  ans['useErr'] = self.thresholdParam (params)
            select = self.kalpha2Select ()
            ans['select'] = select
        
            if select == mess_pk['exec_sel_1']:
                ans['kalpha1'], ans['kalpha2'] = self.kaplha2Param (params)

            self.operationParam (ans, self.param_path)

        exec_space = st.empty ()
        if os.path.exists (self.param_path):
            self.downloadParamFile ()

        with exec_space:
            assert os.path.exists (self.param_path)
            assert os.path.exists (self.hist_path)
            if os.path.exists (self.param_path) & os.path.exists (self.hist_path):
                uploaded_map = self.load_files ()
                #print (st.session_state['uploaded_map'])
                res = self.exec_peaksearch (uploaded_map)
                log = self.request_log ()
      
                result = self.get_result (res)

                if isinstance (result, str):
                    st.write (result)
                elif result is not None:
                    df, peakDf = result
                    ans['df'] = df; ans['peakDf'] = peakDf
                    st.session_state['df'] = df
                    st.session_state['peakDf'] = peakDf
            
    
        return ans
