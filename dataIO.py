import io
import os
import re
import zipfile
import pandas as pd
import xml.etree.ElementTree as ET
import plotly.graph_objects as go
from messages import messages as mess
# streamlitの実行方法 streamlit run ???.py

def read_output_file (path = 'sample2_pks.histogramIgor',
                      lang = 'jpn'):
    df = None; peakdf = None
    with open (path, 'r', encoding='utf-8') as f:
        flg1 = False; flg2 = False; cols1 = None; cols2 = None
        for line in f.readlines ():
            line = line.strip()
            if 'IGOR' in line: continue
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
                line = line.strip().split (' ')
                line = [float (l.strip()) for l in line if len (l) > 0]
                df.append (line)
            elif ('END' in line) & flg2:
                flg2 = False

            elif flg2:
                line = line.strip().split (' ')
                line = [float (l.strip()) for l in line if len (l) > 0]
                peakdf.append (line)
            
            else: continue


    df = list (map (list, zip (*df)))
    peakdf = list (map (list, zip (*peakdf)))
    df = {k:v for k,v in zip (cols1, df)}
    peakdf = {k:v for k,v in zip (cols2, peakdf)}

    mes = mess[lang]['graph']
    df = pd.DataFrame (df)
    peakdf = pd.DataFrame (peakdf)
    peakdf['Flag'] = peakdf['Flag'].apply (lambda x: bool (int (x)))
    
    df.columns = [ 'xphase', 'yphase', 'err_yphase', 'smth_yphase']
    peakdf.columns = [{'eng' : 'Peak', 'jpn' : 'ピーク'}[lang],
                 mes['pos'], mes['peakH'], mes['fwhm'], mes['sel']]    

    return df, peakdf

def show_graph (df, peakDf, lang = 'jpn'):
    mes = mess[lang]['graph']
    fig = go.Figure()
    fig.add_trace (
        go.Scatter (x = df['xphase'], y = df['yphase'],
                    name = mes['diffPattern']))
    fig.add_trace (
        go.Scatter (x = df['xphase'], y= df['smth_yphase'],
                    name = mes['smthCuv']))
    
    fig.add_trace (
        go.Scatter (x = df['xphase'], y = df['err_yphase'],
        name = mes['err']))
    
    fig.add_trace (go.Scatter (
        x = peakDf[mes['pos']], y = peakDf[mes['peakH']],
        mode = 'markers', marker = dict (size = 10, symbol = 'triangle-up'),
        name = mes['peakPos']))

    fig.update_xaxes(title = "2θ") # X軸タイトルを指定
    fig.update_yaxes(title = "Intensity") # Y軸タイトルを指定
    fig.update_layout (showlegend = True)
    #fig.write_html (savePath)
    return (fig)
    
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

def read_inp_xml_conograph (path, root_name = './/ConographParameters'):
    tree = ET.parse(path)  # ファイル名を適宜変更
    root = tree.getroot()
    elem = root.find (root_name)

    ans = elem_to_dict (elem)

    return (ans)





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

    tree.write (path, encoding = 'utf-8', xml_declaration = True)

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

if __name__ == '__main__':
    #path = 'LOG_PEAKSEARCH.txt'
    #print (os.path.exists (path))
    #with open (path, 'r', encoding = 'utf-8') as f:
    #    text = f.read()
    #print (text)

    path = 'docs/allumina.inp.xml'
    params = read_inp_xml_conograph (path)
    print (params)

    
