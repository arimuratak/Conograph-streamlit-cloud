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
    def __init__ (self, lang):
        self.api_url = 'https://conograph-api-server.onrender.com'
        #self.api_url = "http://localhost:8000"
        #self.workSpace = 'PeakSearch'
        
        self.lang = lang
        self.pathSample = 'sample'
        #self.file_uploader = st.session_state
        #self.folder = None
        self.mess = mess[lang]['peaksearch']
        self.param_name = None
        self.hist_name = None
        self.param_path = 'param.imp.xml'
        self.hist_path = 'histogram.txt'
        self.out_path = 'output.txt'
        self.params = None
        #self.objPeakSearch = None
        #self.path_cntl_inp = None
        #self.workSpace = None
        
        #self.param_file = None
        self.hist_file = None
        self.log_path = 'LOG_PEAKSEARCH.txt'
        
        #self.cntl_work_path = None
        #self.param_work_path = None
        #self.hist_work_path = None
        #self.out_work_path = None
        

    #def reset_file_uploader (self,):
    #    if 'upload_files' not in self.file_uploader:
    #        self.file_uploader.upload_files = []
    #    else:
    #        self.file_uploader.upload_files = []

    def down_load_sample (self,):
        zip_bytes = zip_folder (self.pathSample)
        st.download_button (
            label = {
                'eng':'Down load samples (zip format)', 
                'jpn' : 'サンプル ダウンロード (zip形式)'}[self.lang],
            data = zip_bytes,
            file_name = 'sample.zip')

    def display_log (self,):
        with open (self.log_path, 'r', encoding = 'utf-8') as f:
            text = f.read()
        #print (text)
        st.text_area ('log', text, height = 400)

    #------------------------------------------------
    #   upload parameter & histogram file &
    #   save as binary format
    #------------------------------------------------
    def upload_files (self,):
        param_file = st.file_uploader(
                            {'eng' : 'Upload parameter file (xml)',
                            'jpn': 'パラメータファイル (xml) アップロード'}[self.lang],
                            type = ["xml"], key = "param")
        
        hist_file = st.file_uploader(
                            {'eng' : 'Upload histogram file',
                            'jpn': 'ヒストグラムファイル アップロード'}[self.lang],
                            type = ["dat", "histogramIgor", "histogramigor"], key = "hist")

        if param_file:
            self.param_name = param_file.name
            with open (self.param_path, 'wb') as f:
                f.write (param_file.getbuffer ())

            self.params = read_inp_xml (self.param_path)

        if hist_file:
            self.hist_name = hist_file.name
            with open (self.hist_path, 'wb') as f:
                f.write (hist_file.getbuffer ())

    def load_files (self,):
        uploaded_map = {}
        with open (self.param_path, 'rb') as f:
            uploaded_map[self.param_name] = f.read()
        with open (self.hist_path, 'rb') as f:
            uploaded_map[self.hist_name] = f.read ()
        return uploaded_map

    def display_param (self, param_path):
        if st.toggle (
            {'eng' : 'Show Default Parameter',
            'jpn' : 'パラメータ初期値 表示'}[self.lang]):
            text = self.readDefaultParam (param_path)
            st.write (text)

    def exec_peaksearch (self,):
        if st.button ({'eng' : 'Exec','jpn':'実行'}[self.lang]):
            uploaded_map = self.load_files ()
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

    def smthParams (self,):
        st.write (self.mess['smth_mes'])
        col1,col2 = st.columns (2)
        nPointsDefault = self.params[0]['NumberOfPoints'][0]
        endRegionDefault = self.params[0]['EndOfRegion'][0] 
        with col1:
            nPoints = st.text_input (
                self.mess['tbl_col1'],
                nPointsDefault)
        with col2:
            endRegion = st.text_input (
                self.mess['tbl_col2'],
                endRegionDefault)
            
        return (nPoints, endRegion)
    
    def rangeParam (self,):
        st.write (self.mess['area_mes'])
        col1,col2 = st.columns (2)
        rangeMin, rangeMax = self.params[1]
        if rangeMin == 'MIN': rangeMin = 0.0
        with col1:
            minRange = st.text_input ('min', rangeMin)
        with col2:
            maxRange = st.text_input ('max', rangeMax)

        return minRange, maxRange
    
    def thresholdParam (self,):
        st.write (self.mess['th_mes'])
        col1, col2 = st.columns ([2,8])
        c_def, use_error_flg = self.params[2]
        useErrDict = {
            1 : self.mess['th_sel_1'],
            0 : self.mess['th_sel_2']}
        use_error_def = useErrDict [use_error_flg]
        
        with col1:
            c_fixed = st.text_input ('c : ', c_def)
        
        with col2:
            use_error = st.selectbox (
                {'eng' : 'select','jpn' : '選択'}[self.lang],
                options = list (useErrDict.values()))

        return c_fixed, use_error

    def kalpha2Select (self,):
        yes = self.mess['exec_sel_1']
        no = self.mess['exec_sel_2']
        select = st.radio (self.mess['delpk_mes'],
                           [yes, no], horizontal = True)
        return select

    def kaplha2Param (self,):
        mat = np.array ([
            [0.5594075, 0.563798],
            [0.709300, 0.713590],
            [1.540562, 1.544398],
            [1.788965, 1.792850],
            [1.936042, 1.939980],
            [2.289700, 2.293606]])
        kalpha1, kalpha2 = self.params[-1]
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
            self.mess['wavelen_mes'],
            params, index = int (idx))
        
        kalpha1, kalpha2 = sel.split (' / ')[1:]
        #st.write (kalpha1, kalpha2)
        return kalpha1, kalpha2


    def operationParam (self, params, savePath):
        #nPoins = params['nPoints']; endRegion = params['endRegion']
        minRange = params['minRange'] #; maxRange = params['maxRange']
        #c_fixed = params['c_fixed'];
        useErr = params['useErr']
        select = params['select']
        kalpha1 = params['kalpha1']; kalpha2 = params['kalpha2']
        if str (minRange) == '0.0': params['minRange'] = 'MIN'
        params['useErr'] = int (useErr == self.mess['th_sel_1'])
        params['select'] = int (select == self.mess['exec_sel_1'])
        if (kalpha1 == None) | (kalpha2 == None):
            params['kalpha1'], params['kalpha2'] = self.params[-1]

        change_inp_xml (params, savePath)

    def readDefaultParam (self, params):
        text = ''
        smoothing_params = params[0]
        nPoints = smoothing_params['NumberOfPoints'][0]
        endRegion = smoothing_params['EndOfRegion'][0]
        range_begin, range_end = params[1]
        threshold, useErr = params[2]
        alpha2_correction = params[3]
        kalpha1, kalpha2 = params[4]

        text += {'eng':'Smoothing / ', 'jpn' : '平滑化 / '}[self.lang]
        text += self.mess['tbl_col1'] + ' : {}, '.format (nPoints)
        text += self.mess['tbl_col2'] + ' : {}  \n'.format (endRegion)

        text += self.mess['area_mes'] + ' / '
        text += 'min : {}, max : {}  \n'.format (range_begin, range_end)
        text += {'eng':'threshold', 'jpn' : 'しきい値'}[self.lang] + ' / '
        text += 'c : {}, '.format (threshold)
        text += {0 : self.mess['th_sel_2'],
                 1 : self.mess['th_sel_1']
                 }[int (useErr)] + '  \n'

        text += self.mess['delpk_mes'] + ' / '
        text += {0 : self.mess['exec_sel_2'],
                 1 : self.mess['exec_sel_1']
                 }[int (alpha2_correction)] + '  \n'
        
        text += 'kα1 : {}, kα2 : {}'.format (kalpha1, kalpha2)
        return text

    #def updateParamFile (self, ans):
    #    saveParam = st.button (
    #        {'eng' : 'Save parameters',
    #         'jpn':'パラメータ保存'}[self.lang])
    #    if saveParam:
    #        change_inp_xml (ans, self.param_file)

    def downloadParamFile (self,):
        with open (self.param_path, 'rb') as f:
            xml_file = f.read()
        
        st.download_button (
                label = {
                    'eng' : 'Down load new parameters',
                    'jpn' : '新しいパラメータのダウンロード'
                    }[self.lang],
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
        self.reset_files ()
        ans = {k : None for k in [
            'defaultParam', 'df', 'peakDf', 'nPoints', 'endRegion',
            'minRange, maxRange, c_fixed', 'useErr','select',
            'kalpha1', 'kalpha2', 'folder', 'log']}

        self.down_load_sample ()
        self.upload_files ()

        if self.params is not None:
            self.display_param (self.params)

        if self.params is not None:
            ans['nPoints'], ans['endRegion'] = self.smthParams ()
            ans['minRange'], ans['maxRange'] = self.rangeParam ()
            ans['c_fixed'],  ans['useErr'] = self.thresholdParam()
            select = self.kalpha2Select ()
            ans['select'] = select
        
            if select == self.mess['exec_sel_1']:
                ans['kalpha1'], ans['kalpha2'] = self.kaplha2Param ()

            self.operationParam (ans, self.param_path)

        exec_space = st.empty ()
        if os.path.exists (self.param_path):
            self.downloadParamFile ()

        with exec_space:
            if os.path.exists (self.param_path) & os.path.exists (self.hist_path):
                res = self.exec_peaksearch ()
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
