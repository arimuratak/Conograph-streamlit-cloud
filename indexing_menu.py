import streamlit as st
from messages import messages as mess

class IndexingMenu:
    def __init__(self, debug = False):
        self.mess = mess['eng']
        self.param_path = 'param.inp.xml'
        
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

    def display_param (self,):
        lang = st.session_state['lang']
        params = st.session_state['params_idx_defau']
        if st.toggle (
            {'eng' : 'Show Default Parameter',
            'jpn' : 'パラメータ初期値 表示'}[lang]):
            text = self.params2text (params)
            st.write (text)

    def search_level (self,):
        mes, params = self.read_session ()

        selDefault = int (params['SearchLevel'])
        nPeakDefault = params['MaxNumberOfPeaks']
        
        sel1 = mes['quickSearch']
        sel2 = mes['deepSearch']
        select = st.radio (mes['level'],
                           [sel1, sel2], horizontal = True,
                           index = selDefault)
        nPeak = st.text_input (mes['nPeak'], nPeakDefault)

        return select, nPeak
        
    def search_method (self,):
        mes, params = self.read_session ()
        selDef = int (params['IsAngleDispersion'])
        sel1 = mes['tof']; sel2 = mes['angleDisp']
        sel = st.radio (mes['select'],
                        [sel1, sel2], index = selDef,
                        horizontal = True)
        
        if sel == sel1:
            st.write (
                'TOF = c0+c1d+c2d^2+c3d^3+c4d^4+c5d^5')
            col1, col2, col3 = st.columns (3)
            convParams = params['ConversionParameters']

            if len (convParams) > 0: 
                ps = convParams.strip().split (' ')
            else: ps['','','']
            
            with col1: p1 = st.text_input ('', ps[0])
            with col2: p2 = st.text_input ('', ps[1])
            with col3: p3 = st.text_input ('', ps[2])

            ans = [p1, p2, p3]
            
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
            
            ans = [waveLen, zeroPoint]

        sel = {sel1 : '0', sel2 : '1'}[sel]

        return sel, ans
            
    def nPeakForM (self,):
        mes, params = self.read_session ()
        nPeak = params['MaxNumberOfPeaksForFOM']
        
        ans = st.text_input (mes['nPeakForM'], nPeak)

        return ans

    def min_max_miller_idx (self,):
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

        return minIdx, maxIdx

    def minFOM (self,):
        mes, params = self.read_session ()        
        message = mes['minFOM']
        param = params['MinFOM']
        ans = st.text_input (message, param)

        return ans

    def rangeLattice (self,):
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
        return minV, maxV

    def resolution_err (self,):
        mes, params = self.read_session ()
        message = mes['resolution']
        param = params['Resolution']
        ans = st.text_input (message, param)
        return ans

    def select_lattice_pattern (self,):
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
        
        ans = {}
        cols = st.columns (2)
        for i, pattern in enumerate (lattices):
            label = mes[pattern]
            nameOut = self.outputLatticeDict[pattern]
            defV = params[nameOut].strip() == '1'
            with cols[i // 7]:
                state = st.checkbox (label = label,
                            key = 'chk_{}'.format(i), value = defV)
                ans[pattern] = state

        return ans

    def params_precision_search (self,):
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
        param_8 = params['MaxNumberOfSolutionsForEachBravaisLattice']

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
        
        mes8 = mes['maxLatticeConst']
        maxLatticeConst = st.text_input (mes8, param_8, key = '8')

        return (minPrimeCellV, maxLatticeConst, maxNumZone,
                numPrimCell, errQvalue, minMwu, minMrev,
                minDistPoints, maxLatticeConst)




    def menu (self, debug = False):
        if debug:
            st.write ('Under development')
            pass
        lang = st.session_state['lang']


        mes_idx = self.mess['indexing']
        st.write (mes_idx['main'])

        if st.session_state['params_idx_defau'] is not None:
            self.display_param ()

            select, nPeak = self.search_level ()
            print (select, nPeak)

            sel, ans = self.search_method ()
            print (sel, ans)

            nPeak = self.nPeakForM ()
            print (nPeak)

            minIdx, maxIdx = self.min_max_miller_idx ()
            print (minIdx, maxIdx)         

            minFOM = self.minFOM ()
            print (minFOM)

            minV, maxV = self.rangeLattice ()
            print (minV, maxV)

            resolution = self.resolution_err ()
            print (resolution)

            patterns = self.select_lattice_pattern ()
            print (patterns)

            ans = self.params_precision_search ()
            print (ans)        

if __name__ == '__main__':
    from init import setup_session_state
    setup_session_state ()
    idx = IndexingMenu ()
