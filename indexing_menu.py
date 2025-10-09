import os
import time
import pandas as pd
import streamlit as st
import requests
from messages import messages as mess
from dataIO import read_for_bestM, text2lattice, read_peak_indexing,\
                        change_inp_xml_indexing, read_lattices_from_xml

class IndexingMenu:
    def __init__(self,):
        #self.api_url = 'http://localhost:8100'
        self.api_url = 'https://conograph-api-indexing.onrender.com'
        #self.api_url = 'https://conograph-api-indexing-1.onrender.com' # Singapore
        os.makedirs ('input', exist_ok = True)
        os.makedirs ('result', exist_ok = True)

        self.N_bravais_pattern = 14
        self.mess = mess['eng']
        self.param_path = 'input/param.inp.xml'
        self.peak_path = 'result/peakdata.txt'
        self.log_path = 'result/LOG_CONOGRAPH.txt'
        self.result_path = 'result/result.xml'
        self.selected_igor_path = 'result/selected.histogramIgor'
        self.output_zip_path = 'result/output.zip'
        self.lattice_eng2jpn = {
            'Cubic(F)' : '立方晶(F)',
            'Cubic(I)' : '立方晶(I)',
            'Cubic(P)' : '立方晶(P)',
            'Hexagonal' : '六方晶',
            'Rhombohedral' : '三方晶',
            'Tetragonal(I)' : '正方晶(I)',
            'Tetragonal(P)' : '正方晶(P)',
            'Orthorhombic(F)' : '斜方晶(F)',
            'Orthorhombic(I)' : '斜方晶(I)',
            'Orthorhombic(C)' : '斜方晶(C)',
            'Orthorhombic(P)' : '斜方晶(P)',
            'Monoclinic(A)' : '単斜晶(A)',
            'Monoclinic(B)' : '単斜晶(B)',
            'Monoclinic(C)' : '単斜晶(C)',
            'Monoclinic(P)' : '単斜晶(P)',
            'Triclinic' : '三斜晶'}
        
        self.lattice_eng2num = {
            'Cubic(F)' : '14', 'Cubic(I)' : '13',
            'Cubic(P)' : '12', 'Hexagonal' : '11',
            'Rhombohedral' : '10', 'Tetragonal(I)' : '9',
            'Tetragonal(P)' : '8', 'Orthorhombic(F)' : '7',
            'Orthorhombic(I)' : '6', 'Orthorhombic(C)' : '5',
            'Orthorhombic(P)' : '4', 'Monoclinic(A)' : '3',
            'Monoclinic(B)' : '3', 'Monoclinic(C)' : '3',
            'Monoclinic(P)' : '2', 'Triclinic' : '1'
        }
        self.lattice_jpn2num = {
            '立方晶(F)' : '14', '立方晶(I)' : '13',
            '立方晶(P)' : '12', '六方晶' : '11',
            '三方晶' : '10', '正方晶(I)' : '9',
            '正方晶(P)' : '8', '斜方晶(F)' : '7',
            '斜方晶(I)' : '6', '斜方晶(C)' : '5',
            '斜方晶(P)' : '4', '単斜晶(A)' : '3',
            '単斜晶(B)' : '3', '単斜晶(C)' : '3',
            '単斜晶(P)' : '2', '三斜晶' : '1'
        }

        self.lattice2num = {
            'eng' : self.lattice_eng2num,
            'jpn' : self.lattice_jpn2num}
        
        self.lattice_jpn2eng = {
            v : k for k,v in self.lattice_eng2jpn.items()}
        
        self.cvtTbl = {'eng' : self.lattice_jpn2eng,
                       'jpn' : self.lattice_eng2jpn}
        
        self.outputLatticeDict = {
            'tric'    : 'OutputTriclinic',
            'monoc_P' : 'OutputMonoclinicP',
            'monoc_A' : 'OutputMonoclinicA',
            'monoc_B' : 'OutputMonoclinicB',
            'monoc_C' : 'OutputMonoclinicC',
            'ortho_P' : 'OutputOrthorhombicP',
            'ortho_C' : 'OutputOrthorhombicC',
            'ortho_I' : 'OutputOrthorhombicI',
            'ortho_F' : 'OutputOrthorhombicF',
            'tetra_P' : 'OutputTetragonalP',
            'tetra_I' : 'OutputTetragonalI',
            'rhombo'  : 'OutputRhombohedral',
            'hexago'  : 'OutputHexagonal',
            'cubic_P' : 'OutputCubicP',
            'cubic_I' : 'OutputCubicI',
            'cubic_F' : 'OutputCubicF' }
        self.bravais = None

    def set_language (self,):
        if st.session_state['lang'] is not None:
            lang = st.session_state['lang']
            st.session_state['mess_idx'] = mess[lang]['indexing']

    def read_session (self,):
        params = st.session_state['params_idx']
        mes = st.session_state['mess_idx']
        return mes, params

    def params2text (self, params):
        text = []
        for k,v in params.items():
            text.append (k + ' / ' + v)
        ans = '\n'.join (text)
        return ans

    def load_files (self,):
        param_name = st.session_state['param_name']
        peak_name = st.session_state['peak_name']

        uploaded_map = {}
        with open (self.param_path, 'rb') as f:
            uploaded_map[param_name] = f.read()
        with open (self.peak_path, 'rb') as f:
            uploaded_map[peak_name] = f.read ()
        #st.session_state['uploaded_map'] = uploaded_map
        return uploaded_map

    def display_param (self,):
        lang = st.session_state['lang']
        params = st.session_state['params_idx_defau']
        
        if st.toggle (
            {'eng' : 'Show Default Parameter (Indexing)',
            'jpn' : 'パラメータ初期値 表示 (Indexing)'}[lang],
            key = 'display_default_param_indexing'):
            text = self.params2text (params)
            st.write (text)
    
    def exec_indexing (self, uploaded_map):
        lang = st.session_state['lang']
        if st.button ({'eng' : 'Indexing Run',
                       'jpn':'Indexing実行'}[lang]):
            res = self.exec_cmd (uploaded_map, 'quit\n')
            st.session_state['list_candidates'] = None

            return res
        
        return None
    
    def exec_cmd (self, uploaded_map, cmd = None):
        if cmd is None: cmd = 'quit\n'
        elif 'quit' not in cmd[-5:]: cmd += 'quit\n'
        data = {'cmd' : cmd}
        print (cmd)
        files = {}
        for fname, fobj in uploaded_map.items():
                files[fname] = (fname, fobj,
                                'application/octet-stream')

        res = requests.post (
                self.api_url + '/run_cpp', files = files, data = data)

        return res

    def take_indexing_peak_data (self, uploaded_map, numCandidate):
        cmd = numCandidate + '\nquit\n'

        res = self.exec_cmd (uploaded_map, cmd)
        fname = self.request_file ('/get_histogramIgor', self.selected_igor_path)

        selected_lat_peak = read_peak_indexing (self.selected_igor_path)
        st.session_state['peakDf_indexing'] = selected_lat_peak

    def take_indexing_peak_data_selected (self, uploaded_map):
        lang = st.session_state['lang']
        result = st.session_state['result'][lang]
        numCandidate = result['lattice_selected']['number']
        st.session_state['list_candidates'] = [numCandidate]
        paramCandidate = st.session_state['candidate2param'][numCandidate]
        self.take_indexing_peak_data (uploaded_map, paramCandidate)

    def get_fname (self, res):
        fname = res.headers.get ('file_name')
        fname = fname.split('/')[-1]
        return fname

    def request_file (self, add_url = '/log_file', savePath = 'LOG_CONOGRAPH.txt'):
        res = requests.post (
            self.api_url + add_url)
        
        if res is None: ans = None
        else:
            if res.status_code == 200:
                fname = self.get_fname (res)                
                if os.path.exists (savePath):
                    os.remove (savePath)
                
                suffix = fname.split ('.')[-1]
                if suffix in ['txt', 'histoGramIgor', 'xml']:
                    content = res.content.decode ('utf-8')
                    with open (savePath, 'w', encoding = 'utf-8') as f:
                        f.write (content)
                else:
                    with open (savePath, 'wb') as f:
                        f.write (res.content)

                ans = fname
            else:
                ans = 'Error 500'

        return ans


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

    def search_level (self, params_dict):
        mes, params = self.read_session ()

        selDefault = int (params['SearchLevel'])
        nPeakDefault = params['MaxNumberOfPeaks']
        
        sel1 = mes['quickSearch']
        sel2 = mes['deepSearch']
        select = st.radio (mes['level'],
                           [sel1, sel2], horizontal = True,
                           index = selDefault)
        nPeak = st.text_input (mes['nPeak'], nPeakDefault)

        select = {sel1 : '0', sel2 : '1'}[select]
        params_dict['SearchLevel'] = select
        params_dict['MaxNumberOfPeaks'] = nPeak

        return params_dict
        
    def search_method (self, params_dict):
        mes, params = self.read_session ()
        selDef = int (params['IsAngleDispersion'])
        sel1 = mes['tof']; sel2 = mes['angleDisp']
        sel = st.radio (mes['select'],
                        [sel1, sel2], index = selDef,
                        horizontal = True)
        
        params_dict['IsAngleDispersion'] = {
            sel1 : '0', sel2 : '1'}[sel]
        
        ps_dafau = st.session_state['params_idx_defau']
        
        if sel == sel1:
            st.write (
                'TOF = c0+c1d+c2d^2+c3d^3+c4d^4+c5d^5')
            col1, col2, col3 = st.columns (3)
            convParams = params['ConversionParameters']

            if len (convParams) > 0: 
                ps = convParams.strip().split (' ')
            else: ps = [' ',' ',' ']
            
            with col1: p1 = st.text_input (
                'v1', ps[0], key = 'conv1', label_visibility = 'collapsed')
            with col2: p2 = st.text_input (
                'v2', ps[1], key = 'conv2', label_visibility = 'collapsed')
            with col3: p3 = st.text_input (
                'v3', ps[2], key = 'conv3', label_visibility = 'collapsed')

            ans = ' '.join ([p1, p2, p3])

            params_dict['ConversionParameters'] = ans
            params_dict['WaveLength'] = ps_dafau['WaveLength']
            params_dict['ZeroPointShiftParameter'] = ps_dafau['ZeroPointShiftParameter']
            
        else:
            col1, col2 = st.columns (2)
            with col1:
                waveLen = st.text_input (
                                mes['waveLen'],
                                params['WaveLength'])
            with col2:
                zeroPoint = st.text_input (
                        mes['zeroPoint'],
                        params['ZeroPointShiftParameter'])
            
            params_dict['WaveLength'] = waveLen
            params_dict['ZeroPointShiftParameter'] = zeroPoint
            params_dict['ConversionParameters'] = ' '

        return params_dict
            
    def nPeakForM (self, params_dict):
        mes, params = self.read_session ()
        nPeak = params['MaxNumberOfPeaksForFOM']
        
        ans = st.text_input (mes['nPeakForM'], nPeak)

        params_dict['MaxNumberOfPeaksForFOM'] = ans

        return params_dict

    def min_max_miller_idx (self, params_dict):
        mes, params = self.read_session ()
        message = mes['minMaxPeak']
        minN = params['MinNumberOfMillerIndicesInRange']
        maxN = params['MaxNumberOfMillerIndicesInRange']
        st.write (message)
        col1, col2 = st.columns (2)
        with col1:
            minIdx = st.text_input ('min :', minN, key = 'min')
        with col2:
            maxIdx = st.text_input ('max :', maxN, key = 'max')

        params_dict['MinNumberOfMillerIndicesInRange'] = minIdx
        params_dict['MaxNumberOfMillerIndicesInRange'] = maxIdx

        return params_dict

    def minFOM (self, params_dict):
        mes, params = self.read_session ()        
        message = mes['minFOM']
        param = params['MinFOM']
        ans = st.text_input (message, param)

        params_dict['MinFOM'] = ans
        return params_dict

    def rangeLattice (self, params_dict):
        mes, params = self.read_session ()
        message = mes['rangeLattice']
        minRange = params['MinUnitCellEdgeABC']
        maxRange = params['MaxUnitCellEdgeABC']
        st.write (message)
        col1, col2 = st.columns (2)
        with col1:
            minV = st.text_input ('min', minRange, key = 'minRange')
        with col2:
            maxV = st.text_input ('max', maxRange, key = 'maxRange')
        
        params_dict['MinUnitCellEdgeABC'] = minV
        params_dict['MaxUnitCellEdgeABC'] = maxV
        return params_dict

    def resolution_err (self, params_dict):
        mes, params = self.read_session ()
        message = mes['resolution']
        param = params['Resolution']
        ans = st.text_input (message, param)
        params_dict['Resolution'] = ans

        return params_dict

    def select_lattice_pattern (self, params_dict):
        lang = st.session_state['lang']
        st.write ({
            'eng' : 'Output lattice pattern selection',
            'jpn' : '出力格子パターンの選択＞＞'}[lang])
        mes, params = self.read_session ()
        axisMonocliSym = params['AxisForMonoclinicSymmetry'].strip()
        monocABC = 'monoc_' + axisMonocliSym
        lattices = ['tric', 'monoc_P', monocABC,
                    'ortho_P', 'ortho_C', 'ortho_I', 'ortho_F',
                    'tetra_P', 'tetra_I', 'rhombo', 'hexago',
                    'cubic_P', 'cubic_I', 'cubic_F']
        
        cols = st.columns (2)
        for i, pattern in enumerate (lattices):
            label = mes[pattern]
            nameOut = self.outputLatticeDict[pattern]
            defV = params[nameOut].strip() == '1'
            with cols[i // 7]:
                state = st.checkbox (label = label,
                            key = 'chk_{}'.format(i), value = defV)
                params_dict[nameOut] = str (int (state))

        return params_dict

    def params_precision_search (self, params_dict):
        lang = st.session_state['lang']
        st.write (
            {'eng' : '＜＜Parameters for precise indexing＞＞',
            'jpn' : '＜＜指標付け詳細パラメータ＞＞'}[lang])
        
        mes, params = self.read_session ()
        param_1_1 = params['MinPrimitiveUnitCellVolume']
        param_1_2 = params['MaxPrimitiveUnitCellVolume']
        param_2 = params['MaxNumberOfTwoDimTopographs']
        param_3 = params['MaxNumberOfLatticeCandidates']
        param_4 = params['CriticalValueForLinearSum']
        param_5 = params['ThresholdOnNormM']
        param_6 = params['ThresholdOnRevM']
        param_7 = params['MinDistanceBetweenLatticePoints']
        if 'MaxNumberOfSolutionsForEachBravaisLattice' in params:
            param_8 = params['MaxNumberOfSolutionsForEachBravaisLattice']
        else: param_8 = None
        
        mes1 = mes['threshPrim']
        st.write (mes1)
        col1_1, col1_2 = st.columns (2)
        with col1_1:
            minPrimeCellV = st.text_input ('min', param_1_1, key = '1_1')
        with col1_2:
            maxPrimeCellV = st.text_input ('max', param_1_2, key = '1_2')

        mes2 = mes['maxNumZone']
        maxNumZone = st.text_input (mes2, param_2, key = '2')

        mes3 = mes['numPrimCell']
        numPrimCell = st.text_input (mes3, param_3, key = '3')
        
        mes4 = mes['v4linearSum']
        errQvalue = st.text_input (mes4, param_4, key = '4')

        mes5 = mes['minMwu']
        minMwu = st.text_input (mes5, param_5, key = '5')

        mes6 = mes['minMrev']
        minMrev = st.text_input (mes6, param_6, key = '6')

        mes7 = mes['minDistPoints']
        minDistPoints = st.text_input (mes7, param_7, key = '7')
        
        if param_8 is not None:
            mes8 = mes['maxLatticeConst']
            maxLatticeConst = st.text_input (mes8, param_8, key = '8')
        else: maxLatticeConst = None

        params_dict[
            'MinPrimitiveUnitCellVolume'] = minPrimeCellV
        params_dict[
            'MaxPrimitiveUnitCellVolume'] = maxPrimeCellV
        params_dict[
            'MaxNumberOfTwoDimTopographs'] = maxNumZone
        params_dict[
            'MaxNumberOfLatticeCandidates'] = numPrimCell
        params_dict[
            'CriticalValueForLinearSum'] = errQvalue
        params_dict[
            'ThresholdOnNormM'] = minMwu
        params_dict[
            'ThresholdOnRevM'] = minMrev
        params_dict[
            'MinDistanceBetweenLatticePoints'
                                        ] = minDistPoints
        if maxLatticeConst is not None:       
            params_dict[
                'MaxNumberOfSolutionsForEachBravaisLattice'
                                        ] = maxLatticeConst
        
        return params_dict
    
    def to_jpn (self, eng):
        if eng not in self.lattice_eng2jpn:
            return eng
        return self.lattice_eng2jpn[eng] 

    # bestM, lattice constant, lattice selected, lattice candidatesの
    # 結果を和英両方を設定
    def put_result_jpn_eng (self,
            df_bestM, txt_bestM, dict_bestM, latConst,
            lattice_selected, lattice_candidates):
        
        eng = { 'df_bestM' : df_bestM, 'txt_bestM' : txt_bestM,
                'dict_bestM' : dict_bestM, 'latConst' : latConst,
                'lattice_selected' : lattice_selected,
                'lattice_candidates' : lattice_candidates }
        
        df_jp = df_bestM.copy()
        df_jp['CrystalSystem'] = df_jp[
                            'CrystalSystem'].apply (self.to_jpn)
        txt_jp = []
        for txt in txt_bestM:
            t1, t2 = txt.split (':')
            t1 = t1.strip(); t2 = t2.strip()
            txt_jp.append (' : '.join ([self.to_jpn (t1), t2]))
        
        dict_jp = {
            self.to_jpn (k) : v for k, v in dict_bestM.items()}
        lat_jp = latConst.copy()
        lat_jp['CrystalSystem'] = lat_jp[
            'CrystalSystem'].apply (self.to_jpn)

        sel_jp = lattice_selected
        sel_jp['CrystalSystem'] = self.to_jpn (sel_jp['CrystalSystem'])

        cand_jp = lattice_candidates.copy()
        cand_jp['CrystalSystem'] = cand_jp['CrystalSystem'].apply (self.to_jpn)

        jpn = {'df_bestM' : df_jp, 'txt_bestM' : txt_jp,
                'dict_bestM' : dict_jp, 'latConst' : lat_jp,
                'lattice_selected' : sel_jp,
                'lattice_candidates' : cand_jp}
        
        result = {'eng' : eng, 'jpn' : jpn}

        st.session_state['result'] = result 

    def candidates2cvttbl (self, df):
        df['num_cs'] = df['CrystalSystem'].apply (
            lambda x : self.lattice_eng2num[x])
        df['Parameters'] = df['num_cs'] + ' ' + df['OptimizedParameters']
        
        cvtTbl = {}
        for _, row in df.iterrows():
            cvtTbl[row['number']] = row['Parameters']

        return cvtTbl

    def get_result(self, res):
        ans = None  # ← これで常に定義済みにしておく

        if res is None:
            return ans  # None を返す

        try:
            status = getattr(res, "status_code", None)

            if status == 200:
                # 既存ファイルを安全に差し替え
                if os.path.exists(self.result_path):
                    os.remove(self.result_path)
                with open(self.result_path, "wb") as f:
                    f.write(res.content or b"")

                df_bestM, txt_bestM, dict_bestM, candi_exists = read_for_bestM(self.result_path)
                latConst = text2lattice(dict_bestM)
                selected_lattice, lattice_candidates = read_lattices_from_xml(self.result_path)
                cvtTbl = self.candidates2cvttbl (lattice_candidates)
                st.session_state['candidate2param'] = cvtTbl
                self.put_result_jpn_eng(
                    df_bestM, txt_bestM, dict_bestM, latConst,
                    selected_lattice, lattice_candidates)
                st.session_state['candidate_exist'] = candi_exists
                ans = candi_exists

            elif status == 500:
                ans = "Error 500"

            else:
                # 他のHTTPコード（404や502など）の場合のフォールバック
                ans = f"HTTP {status}"

        except Exception as e:
            # 解析処理やファイル書き込みで例外が出た場合も返せるようにする
            ans = f"Exception: {type(e).__name__}: {e}"

        return ans


    # パラメータ設定メニュー
    def param_menu (self,):
        lang = st.session_state['lang']
        newParams = {}

        # toggleが選択されなければ、newParamsは空のまま
        # toggleが選択されれば、newParamsにはメニューで
        # 選択されたパラメータが入る
        with st.expander (
            {'eng' : 'Open parameter menu (Indexing)',
             'jpn' : 'パラメータメニュー (Indexing)'}[lang]):
            newParams = self.search_level (newParams)
            
            newParams = self.search_method (newParams)

            newParams = self.nPeakForM (newParams)

            newParams = self.min_max_miller_idx (newParams)

            newParams = self.minFOM (newParams)

            newParams = self.rangeLattice (newParams)

            newParams = self.resolution_err (newParams)

            newParams = self.select_lattice_pattern (newParams)

            newParams = self.params_precision_search (newParams) 

        return newParams

    def menu (self, ):
        if st.session_state['params_idx_defau'] is not None:
            #self.display_param ()
            
            with st.container (border = True):
                newParams = self.param_menu ()
                exec_space = st.empty ()

            if len (newParams) > 0:
                change_inp_xml_indexing (newParams, self.param_path)

            if os.path.exists (self.param_path) & os.path.exists (self.peak_path):
                uploaded_map = self.load_files()
    
                with exec_space:
                    res = self.exec_indexing (uploaded_map)

                result = self.get_result (res)
                if isinstance (result, str):
                    st.write (res)

                elif result is not None:
                    if result:
                        self.take_indexing_peak_data_selected (
                                                    uploaded_map)
                        st.session_state['menu_indexing'] = True
                        st.session_state['menu_peaksearch'] = False

                    else:
                        st.session_state['peakDf_indexing'] = None
                        st.session_state['menu_indexing'] = True
                        st.session_state['menu_peaksearch'] = False

    def disp_bestM (self,):
        lang = st.session_state['lang']
        result = st.session_state['result'][lang]
        df_bestM = result['df_bestM']
        txt_bestM = result['txt_bestM']
        dict_bestM = result['dict_bestM']
        st.table (df_bestM)
        sel = st.selectbox (
            {'eng' : 'Select Bravais Lattice..',
            'jpn' : 'ブラベー格子の選択'}[lang],
            txt_bestM)
        sel = sel.split(':')[0].strip()
        col1, col2 = st.columns (2)
        with col1:
            st.write (
                {'eng' : 'Selected Bravais lattice : ',
                 'jpn' : '選択されたブラベー格子 : '}[lang])
        with col2:
            st.write (sel)

        text = dict_bestM[sel]
        text = text.replace ('\n', '  \n')
        st.markdown (text)

    def disp_lattice_consts (self,):
        lang = st.session_state['lang']
        result = st.session_state['result'][lang]
        df = result['latConst']
        st.table (df)

    def to_float (self, vstr):
        if vstr == '-': return vstr
        return str (float (vstr))

    def build_candidate_df (self,):
        lang = st.session_state['lang']
        df = st.session_state['result'][lang]['lattice_candidates']
        df = df.rename (
            columns = {
                'FigureOfMeritWolff' : 'M',
                'FigureOfMeritWu' : 'Mwu',
                'ReversedFigureOfMeritWolff' : 'Mrev',
                'SymmetricFigureOfMeritWolff' : 'Msym',
                'NumberOfLatticesInNeighborhood' : 'NN',
                })
        
        df['M'] = df['M'].apply (self.to_float)
        df['Mwu'] = df['Mwu'].apply (self.to_float)
        df['Mrev'] = df['Mrev'].apply (self.to_float)
        df['Msym'] = df['Msym'].apply (self.to_float)
        df['OptimizedParameters'] = df['OptimizedParameters'].apply (
            lambda ps: ', '.join ([self.to_float(p) for p in ps.split()]))

        values = df.loc[:, ['M', 'Mwu', 'Mrev', 'Msym', 'NN',
                     'OptimizedParameters']].values
        values = [', '.join (vs[:-1]) + '; ' + vs[-1] for vs in values]
        
        df['for_menu'] = values
        if df['M'].unique()[0] != '-':
            df['M'] = df['M'].apply (float)

        return df

    def menu_select_candidate (self,):
        lang = st.session_state['lang']
        css = {'eng' : list (self.lattice_eng2jpn.keys()),
                'jpn' : list (self.lattice_eng2jpn.values())}[lang]

        df = self.build_candidate_df ()
        text = 'M, Mwu, Mrev, Msym, NN; a, b, c, α, β, γ'
        st.write ({'eng' : 'Bravais lattice  : ',
                'jpn' : 'ブラベー格子 : '}[lang] + text)
        
        numSelectedCandidate =\
            st.session_state['result'][lang]['lattice_selected']['number']
        
        for cs in css:
            params = df.loc[df['CrystalSystem'] == cs]
            if len (params) == 0:
                st.write (cs)
            else:
                params = params.sort_values('M', ascending = False)
                sels = params['for_menu'].tolist()
                nums = params['number'].tolist()
                sel_dict = {sel  : num for sel, num in zip (sels, nums)}

                sels = ['-----'] + sels

                if numSelectedCandidate in nums: idx = 1
                else: idx = 0

                sel = st.selectbox (cs, sels, index = idx, # = idx
                                    key = cs)
                self.manage_list_candidates (sel, sel_dict)
        
        if (st.session_state['list_candidates'] is not None
            ) and (len (st.session_state['list_candidates']) > 1):
            selected_num = st.session_state['list_candidates'][-1]
            if selected_num != numSelectedCandidate:
                uploaded_map = self.load_files ()
                selectedParam = st.session_state['candidate2param'][selected_num]
                fname = self.take_indexing_peak_data (uploaded_map, selectedParam)
                
    def operation_summary (self,):
        lang = st.session_state['lang']
        flg = st.button (
            {'eng' : 'Get histogramIgor files after refinement...',
             'jpn' : '細密化されたhistogramIgorファイルの入手'}[lang])
        if flg:
            res = self.exec_summary ()
            self.download_output (res)

    def exec_summary (self,):
        cmd = st.session_state['list_candidates']
        cvt = st.session_state['candidate2param']
        cmd = [cvt[c] for c in cmd]
        cmd = '\n'.join (cmd) + '\nquit\n'
        uploaded_map = self.load_files()
        res = self.exec_cmd (uploaded_map, cmd)
        res = self.request_file (
            add_url= '/get_output_zip',
            savePath = self.output_zip_path)
        return res

    def download_output (self, res):
        if (res is not None) and (res != 'Error 500'):
            lang = st.session_state['lang']
            with open (self.output_zip_path, 'rb') as f:
                zip_file = f.read()

            st.download_button (
                {'eng' : 'Download data',
                 'jpn' : 'ダウンロードデータ'}[lang],
                data = zip_file,
                file_name = self.output_zip_path
            )

    def manage_list_candidates (self, sel, sel_dict):
        # sel_dict : 格子パターン毎の候補番号&格子定数
        # nums : 格子パターンに含まれてる格子番号list
        #nums = list (sel_dict.values())

        #list_candidates = st.session_state['list_candidates']
        #list_candidatesには、他の格子パターンの候補番号が格納されている
        #selected_num = list_candidates.pop (0) #selectedLatticeCandidateの候補番号

        # 
        #list_candidates = [n for n in list_candidates if n not in nums]
        
        if sel != '-----':
            sel = sel_dict[sel]
            if sel not in st.session_state['list_candidates']:
                st.session_state['list_candidates'].append (sel)            

        #list_candidates = [selected_num] + list_candidates

        #st.session_state['list_candidates'] = list_candidates

    def display_log (self,):
        with open (self.log_path, 'r', encoding = 'utf-8') as f:
            text = f.read()
        st.text_area ('log', text, height = 400)

if __name__ == '__main__':
    from init import setup_session_state
    setup_session_state ()
    idx = IndexingMenu ()
