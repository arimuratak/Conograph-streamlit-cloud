import io
import os
import time
import re
import zipfile
import pandas as pd
import xml.etree.ElementTree as ET
from lxml import etree
import plotly.graph_objects as go
from collections import defaultdict
from messages import messages as mess
# streamlitの実行方法 streamlit run ???.py

def read_peak_indexing (path, yvalue = -500):
    header = 'WAVES/O dphase_0, xphase_0, yphase_0, h_0, k_0, l_0'
    cols = [col.strip(',') for col in header.split()[1:]]

    end = 'END'
    df = []; flg = False
    with open (path, 'r', encoding = 'utf-8') as f:
        for line in f.readlines ():
            line = line.strip()
            if len (line) == 0: continue
            if (not flg) & (header in line):
                flg = True
            elif flg & ('BEGIN' in line): continue
            elif flg & (end in line):
                break

            elif flg:
                line = line.split()
                df.append (line)

            else: continue
    
    df = list (map (list, zip (*df)))
    df = pd.DataFrame ({k : v for k,v in zip (cols, df)})
    df = df.loc[:, ['xphase_0', 'h_0', 'k_0', 'l_0']
        ].rename (columns = {'xphase_0' : 'peakpos',
                             'h_0' : 'h', 'k_0' : 'k',
                             'l_0' : 'l'})
    df['peakpos'] = df['peakpos'].apply (float)
    df['h'] = df['h'].apply (int)
    df['k'] = df['k'].apply (int)
    df['l'] = df['l'].apply (int)
    
    
    df['hkl'] = list (df[['h', 'k', 'l']].values)
    
    df = df.drop (['h', 'k', 'l'], axis = 1)

    df['flg'] = df['hkl'].apply (lambda hkl: any (hkl < 0))
    df['y'] = yvalue

    return df

def histogram_file_check (path = 'sample2_pks.histogramIgor'):
    flg = True
    try:
        with open (path, 'r', encoding = 'utf-8') as f:
            text = f.read()
    except:
        flg = False

    if flg:
        flg &= 'IGOR' in text
        flg &= 'WAVES/O' in text
        flg &= 'BEGIN' in text
        flg &= 'END' in text

    return flg        

def read_histo_file (path = 'sample2_pks.histogramIgor',
                      lang = 'eng'):
    flg = histogram_file_check (path)
    if not flg: return None, None

    df = None; peakdf = None
    with open (path, 'r', encoding='utf-8') as f:
        flg1 = False; flg2 = False; cols1 = None; cols2 = None
        for line in f.readlines ():
            line = line.strip()
            
            if 'IGOR' in line: continue
            #elif n_end == 2: break
            elif 'WAVES/O' in line:
                line = line.replace ('WAVES/O', '').strip()
                if cols1 is None: cols1 = line.split (', ')
                else: cols2 = line.split(', ')
            elif ('BEGIN' in line) & (df is None):
                flg1 = True
                df = []
            elif ('BEGIN' in line) & (peakdf is None):
                flg2 = True
                peakdf = []
            elif ('END' in line) & flg1:
                flg1 = False
            elif flg1:
                if len (line) == 0: continue
                line = line.split ()
                line = [float (l) for l in line if len (l) > 0]
                df.append (line)
            elif ('END' in line) & flg2:
                flg2 = False
                break

            elif flg2:
                if len (line) == 0: continue
                line = line.split ()
                line = [float (l) for l in line if len (l) > 0]
                peakdf.append (line)
            
            else: continue
    
    df = list (map (list, zip (*df)))
    df = {k:v for k,v in zip (cols1, df)}
    df = pd.DataFrame (df)
    cols = [ 'xphase', 'yphase', 'err_yphase', 'smth_yphase']
    colLen = min (len (cols), len (df.columns))
    cols = cols[:colLen]
    df = df.loc[:, df.columns[:colLen]]
    df.columns = cols
    #if len (cols1) == 4:
    #    df.columns = [ 'xphase', 'yphase', 'err_yphase', 'smth_yphase']
    #else:
    #    df.columns = cols1
    
    if peakdf is not None:
        peakdf = list (map (list, zip (*peakdf)))
        peakdf = {k:v for k,v in zip (cols2, peakdf)}

        mes = mess[lang]['graph']
        peakdf = pd.DataFrame (peakdf)
    
        peakdf['Flag'] = peakdf['Flag'].apply (lambda x: bool (int (x)))
    
    
        peakdf.columns = [{'eng' : 'Peak', 'jpn' : 'ピーク'}[lang],
                 mes['pos'], mes['peakH'], mes['fwhm'], mes['sel']]    

    return df, peakdf

def show_graph (df, peakDf, peakDf_index = None, lang = 'jpn'):
    mes = mess[lang]['graph']
    fig = go.Figure()
    fig.add_trace (
        go.Scatter (x = df['xphase'], y = df['yphase'],
                    name = mes['diffPattern']))
    
    if 'smth_yphase' in df.columns:
        fig.add_trace (
            go.Scatter (x = df['xphase'], y= df['smth_yphase'],
                    name = mes['smthCuv']))
        
    fig.add_trace (
        go.Scatter (x = df['xphase'], y = df['err_yphase'],
        name = mes['err']))

    if peakDf is not None:
        if 'Flag' in peakDf.columns:
            peakDf = peakDf.loc[peakDf['Flag'] == '1']    
        fig.add_trace (go.Scatter (
            x = peakDf[mes['pos']], y = peakDf[mes['peakH']],
            mode = 'markers',
            marker = dict (size = 10, symbol = 'triangle-up'),
            name = mes['peakPos']))

    if (peakDf_index is not None) & (peakDf is not None):
        maxH = peakDf[mes['peakH']].max(); 
        y0 = - maxH / 30; y1 = y0 - maxH / 20
            
        shapes = [
            dict (type = 'line', x0 = pos, x1 = pos,
                y0 = y0, y1 = y1,
                line = dict (color = 'red', width = 1))
            for pos in peakDf_index['peakpos'].tolist()]
        fig.update_layout(shapes = shapes)

    fig.update_xaxes(title = '2θ') # X軸タイトルを指定
    fig.update_yaxes(title = 'Intensity') # Y軸タイトルを指定
    fig.update_layout (showlegend = True)
    #fig.write_html (savePath)
    return fig
    
def read_cntl_inp_xml (path):
    # XMLファイルを読み込む
    tree = ET.parse(path)  # ファイル名を適宜変更
    root = tree.getroot()

    # 各要素の取得
    control_param = root.find('.//ControlParamFile')
    control_param_file = control_param.text.strip() if control_param is not None else None

    histogram_file = root.find('.//HistogramDataFile/FileName')
    histogram_file_name = histogram_file.text.strip() if histogram_file is not None else None

    outfile = root.find('.//Outfile')
    outfile_name = outfile.text.strip() if outfile is not None else None
    return control_param_file, histogram_file_name, outfile_name

def read_inp_xml (path):
    # XMLファイルを読み込む
    tree = ET.parse(path)  # 適宜ファイル名を変更
    root = tree.getroot()

    # PeakSearchPSParameters セクション
    ps_params = root.find('.//PeakSearchPSParameters')

    # ParametersForSmoothingDevision（複数ある場合に備えてリストで取得）
    smoothing_params = {
        'NumberOfPoints' : [],
        'EndOfRegion' : []             }
    for div in ps_params.findall('.//ParametersForSmoothingDevision'):
        num_points = div.find('NumberOfPointsForSGMethod').text.strip()
        end_region = div.find('EndOfRegion').text.strip()
        smoothing_params['NumberOfPoints'].append (int (num_points))
        smoothing_params['EndOfRegion'].append (end_region)

    # PeakSearchRange
    range_begin = ps_params.find('.//PeakSearchRange/Begin').text.strip()
    range_end = ps_params.find('.//PeakSearchRange/End').text.strip()

    # UseErrorData
    use_error_data = ps_params.find('UseErrorData').text.strip()

    # Threshold
    threshold = ps_params.find('Threshold').text.strip()

    # Alpha2Correction
    alpha2_correction = ps_params.find('Alpha2Correction').text.strip()

    # Waves
    kalpha1 = ps_params.find('.//Waves/Kalpha1WaveLength').text.strip()
    kalpha2 = ps_params.find('.//Waves/Kalpha2WaveLength').text.strip()

    params = {
        'nPoints' : smoothing_params['NumberOfPoints'][0],
        'endRegion' : smoothing_params['EndOfRegion'][0],
        'minRange' : range_begin, 'maxRange' : range_end,
        'c_fixed' : float (threshold),
        'useErr' :int (use_error_data),
        'select' : int (alpha2_correction),
        'kalpha1' : float (kalpha1), 'kalpha2' : float (kalpha2)}
    
    return params

def elem_to_dict(elem):
    children = list(elem)
    if not children:
        return (elem.text or '').strip()
    result = {}
    for child in children:
        key = child.tag
        value = elem_to_dict(child)
        if key in result:
            # 同じタグ名の要素が複数ある場合、リストにまとめる
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(value)
        else:
            result[key] = value
    return result

def read_inp_xml_conograph (
        path, root_name = './/ConographParameters'):
    tree = ET.parse(path)  # ファイル名を適宜変更
    root = tree.getroot()
    elem = root.find (root_name)

    ans = elem_to_dict (elem)

    return (ans)

def parameter_file_check (
        path, root_name = 'ZCodeParameters',
        name_1 = 'ConographParameters',
        name_2 = 'PeakSearchPSParameters'):
    
    tree = ET.parse (path)
    root = tree.getroot ()
    
    if root_name in root.tag:
        childs = [child.tag for child in root]
        ans = (name_1 in childs) & (name_2 in childs)
    else: ans = False

    return ans

def read_for_bestM (path):
    with open (path, 'rb') as f:
        tree = etree.parse (f)
        comments = tree.xpath('//comment()')

    # Information on the best M solution for each Bravais type.
    com1 = comments[0].text
    # Labels of the solution with the best figure of merit.
    com2 = comments[1].text
    df, texts = bestM_1 (com1)
    ans = bestM_2 (com2)

    cand_exists = df['TNB'].apply (int).sum() > 0

    return df, texts, ans, cand_exists

def arrange_sep (text, sep = ', '):
    ts = text.split (':')
    ts_1 = ts[0]; ts_2 = ts[1].strip()
    ts_2 = sep.join (ts_2.split())
    ans = ' : '.join ([ts_1, ts_2])
    return ans


# Read index.xml comment of
# CrystalSystem', 'TNB', 'M', 'Mwu', 'Mrev', 'Msym', 'NN', 'VOL'
def bestM_1 (texts):
    texts = texts.split ('\n')
    texts = [t.strip() for t in texts]
    texts = texts[9:23]
    cols = ['CrystalSystem', 'TNB', 'M', 'Mwu', 'Mrev', 'Msym', 'NN', 'VOL']
    valList = []; maxLen = len(cols) #0
    for text in texts:
        text = text_sci2fixed (text)
        text = text.replace (':', '').split()
        valList.append (text)
        maxLen = max (maxLen, len (text))

    valList = [val + ['' for _ in range (maxLen - len (val))] for val in valList]

    df = pd.DataFrame (data = valList, columns= cols)

    #texts = [reduce_space(text) for text in texts]
    texts = [text_sci2fixed (text) for text in texts]
    texts = [arrange_sep (text) for text in texts]

    return df, texts

def reduce_space (text):
    text = text.split()
    return ' '.join (text)

def text2lattice (ans):
    df = []
    for cs, text in ans.items():
        if '- - : - -' in text:
            #text = [cs] + ['-' for _ in range (6)] + ['0']
            text = [cs, '-', '-', '-', '-', '-', '-', '0']
            df.append (text) 
        else:
            text = text.split ('\n')
            df += [[cs] + t.split(':')[1].split() for t in text]

    cols = ['CrystalSystem', 'a', 'b', 'c', 'alpha', 'beta', 'gamma', 'candidate']
    df = pd.DataFrame (data = df, columns = cols)
    
    count = df['candidate'].value_counts().reset_index()
    count.columns = ['candidate', 'N']
    df = pd.merge (df, count, on = 'candidate', how = 'left')
    countDf = df.sort_values (['candidate', 'N'], ascending = True)
    countDf = countDf.groupby ('CrystalSystem')[['candidate','N']].agg(list)
    countDf = countDf['candidate'].apply (lambda x: x[0])
    df = pd.merge (df, countDf,
                   on = ['CrystalSystem','candidate'], how = 'right')
    df = df.drop_duplicates()
    
    return df.drop (['candidate', 'N'], axis = 1)

def sci2fixed (match):
    return (str (float (match.group())))

def text_sci2fixed (text):
    ans = re.sub(r'[-+]?\d*\.\d+e[-+]\d+', sci2fixed, text)
    return ans

# Read index.xml comment of
# CrystalSystem', 'Best score', 'Lattice constatnts' 'lLabel'
def bestM_2 (texts):
    texts = texts.split ('\n')[1:]
    texts = [t.strip() for t in texts if len (t) > 0] #Except of Empty space
    
    ans = {}; key = ''
    for i, text in enumerate (texts):
        if len (text) == 0: continue
        if i % 6 == 0:
            key = text.split (',')[0]
            ans[key] = []
        elif i % 6 <= 3:
            #text = reduce_space (text)
            if '- - : - -' not in text:
                text = text_sci2fixed (text)
                text = arrange_sep (text)
            ans[key].append (text)
            #ans[key].append (reduce_space (text))

        if i % 6 == 3:
            ans[key] = '\n'.join (ans[key])
        
    return ans

def to_jpn (df, texts, ans, latticeConst, cvtTbl):
    df['CrystalSystem'] = df['CrystalSystem'].apply (lambda x: cvtTbl[x])
   
    tmp = texts
    texts = []
    for t in tmp:
       cs = t.split (':')[0].strip()
       t = t.replace (cs, cvtTbl[cs])
       texts.append (t)

    ans = {cvtTbl[k] : v for k,v in ans.items()}

    latticeConst['CrystalSystem'] = latticeConst['CrystalSystem'].apply (lambda x: cvtTbl[x])

    return df, texts, ans, latticeConst 

def extract_candidate(elem):
    ans = {
        "number": elem.attrib.get("number"),
        "CrystalSystem": elem.findtext("CrystalSystem"),
        "OptimizedParameters": elem.findtext("OptimizedLatticeParameters"),
        "FigureOfMeritWolff": elem.findtext("FigureOfMeritWolff"),
        "FigureOfMeritWu": elem.findtext("FigureOfMeritWu"),
        "ReversedFigureOfMeritWolff": elem.findtext("ReversedFigureOfMeritWolff"),
        "SymmetricFigureOfMeritWolff": elem.findtext("SymmetricFigureOfMeritWolff"),
        "NumberOfLatticesInNeighborhood": elem.findtext("NumberOfLatticesInNeighborhood"),
    }
    
    return ans

def read_lattices_from_xml (path = 'result.xml'):
    tree = ET.parse (path)
    root = tree.getroot () # ConographOutput

    target = 'SelectedLatticeCandidate'
    flg = any ([elem.tag == target for elem in root.iter()])
    
    if not flg:
        selected = {
            'number': '-',
            'CrystalSystem': '-',
            'OptimizedParameters': '-',
            'FigureOfMeritWolff': '-',
            'FigureOfMeritWu': '-',
            'ReversedFigureOfMeritWolff': '-',
            'SymmetricFigureOfMeritWolff': '-',
            'NumberOfLatticesInNeighborhood': '-'}
        
        candidates = pd.DataFrame (
            {key : [val] for key, val in selected.items()})
        
        return selected, candidates 

    selected = root.find ('.//SelectedLatticeCandidate')
    selected = extract_candidate (selected)
    selected = {k : v.strip() for k,v in selected.items()}

    candidates = []
    for cand in root.findall ('.//LatticeCandidate'):
        if cand is None: continue
        cand = extract_candidate (cand)
        if cand['CrystalSystem'] is None: continue
        cand = {k : v.strip() for k,v in cand.items()}
        candidates.append (cand)

    return selected, pd.DataFrame (candidates)

def change_inp_xml (params, path):
    # params : {num_points : , end_region : ,
    #           range_begin : , range_end : ,
    #           use_error : , threshold : , alpha2corr : ,
    #           kalpha1 : , kalpha2 :}
    tree = ET.parse(path)  # 適宜ファイル名を変更
    root = tree.getroot()

    # PeakSearchPSParameters セクション
    ps_params = root.find('.//PeakSearchPSParameters')

    # ParametersForSmoothingDevision（複数ある場合に備えてリストで取得）
    for div in ps_params.findall('.//ParametersForSmoothingDevision'):
        div.find('NumberOfPointsForSGMethod').text = str (params['nPoints'])
        div.find('EndOfRegion').text = params['endRegion']
    

    # PeakSearchRange
    ps_params.find('.//PeakSearchRange/Begin').text = params['minRange']
    ps_params.find('.//PeakSearchRange/End').text = params['maxRange']

    # UseErrorData
    ps_params.find('UseErrorData').text = str (params['useErr'])

    # Threshold
    ps_params.find('Threshold').text = str (params['c_fixed'])

    # Alpha2Correction
    ps_params.find('Alpha2Correction').text = str (params['select'])

    # Waves
    ps_params.find('.//Waves/Kalpha1WaveLength').text = str (params['kalpha1'])
    ps_params.find('.//Waves/Kalpha2WaveLength').text = str (params['kalpha2'])

    tree.write (path, encoding = 'utf-8',
                xml_declaration = True)

def change_inp_xml_indexing (params, path):
    # params : {
    # SearchLevel, MaxNumberOfPeaks, IsAngleDispersion,
    # ConversionParameters, WaveLength,
    # ZeroPointShiftParameter, MaxNumberOfPeaksForFOM,
    # MinNumberOfMillerIndicesInRange,
    # MaxNumberOfMillerIndicesInRange, MinFOM,
    # MinUnitCellEdgeABC, MaxUnitCellEdgeABC,
    # Resolution,
    # MinPrimitiveUnitCellVolume, MaxPrimitiveUnitCellVolume,
    # MaxNumberOfTwoDimTopographs, MaxNumberOfLatticeCandidates,
    # CriticalValueForLinearSum, ThresholdOnNormM,
    # ThresholdOnRevM }
    tree = ET.parse (path)
    root = tree.getroot ()
    ps = root.find ('.//ConographParameters')

    for k, v in params.items():
        ps.find (k).text = v

    tree.write (path, encoding = 'utf-8',
                xml_declaration = True)


def zip_folder(folder_path):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)
    zip_buffer.seek(0)
    return zip_buffer

def correct_parameter_datas (folder = 'sample_', savePath = 'all_parameters.csv'):
    dfs = {'names' : [], 'params_pks' : [], 'params_idx' : []}
    for dir, _, files in os.walk (folder):
        if len (files) > 0:
            for fname in files:
                if ('inp.xml' in fname) & (fname != 'cntl.inp.xml'):
                    name = fname.split ('.')[0]
                    path = os.path.join (dir, fname)
                    params_pks = read_inp_xml (path)
                    params_idx = read_inp_xml_conograph (path)

                    dfs['names'].append (name)
                    dfs['params_pks'].append (params_pks)
                    dfs['params_idx'].append (params_idx)

    params = {'names' : []}
    names_pks = []; names_idxs = []
    for pks in dfs['params_pks'][0].keys():
        names_pks.append (pks)
        params[pks] = []
    for idxs in dfs['params_idx'][0].keys():
        names_idxs.append (idxs)
        params[idxs] = []
    
    for name, pks, idxs in zip (dfs['names'], dfs['params_pks'], dfs['params_idx']):
        params['names'].append (name)
        for  name_pk in names_pks:
            if name_pk in pks:
                params[name_pk].append (pks[name_pk])
            else:
                params[name_pk].append (None)

        for name_idx in names_idxs:
            if name_idx in idxs:
                params[name_idx].append (idxs[name_idx])
            else:
                params[name_idx].append (None)    
        
    params = pd.DataFrame (params).transpose()
    params.to_csv (savePath)

if __name__ == '__main__':
    #ans1, ans2 = read_lattices_from_xml ('result/result.xml')
    #print (ans1)
    #print (ans2)
    df, texts, ans, flg = read_for_bestM ('result/result.xml')
    print (df)
    print (texts)
    print (ans)
    print (flg)
    ##ans = text2lattice (ans)
    #print (ans)
    #correct_parameter_datas (
    #    folder = 'sample_', savePath = 'all_parameters.csv')


