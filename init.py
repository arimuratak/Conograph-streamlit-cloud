import streamlit as st

def setup_session_state ():
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
    if 'peakDf_selected' not in st.session_state:
        st.session_state['peakDf_selected'] = None
    if 'sel_graph' not in st.session_state:
        st.session_state['sel_graph'] = None

    if 'mess_idx' not in st.session_state:
        st.session_state['mess_idx'] = None
    if 'params_idx' not in st.session_state:
        st.session_state['params_cono'] = None
    if 'params_idx_defau' not in st.session_state:
        st.session_state['params_idx_defau'] = None
    if 'params_idx' not in st.session_state:
        st.session_state['params_idx'] = None
    if 'bravais' not in st.session_state:
        st.session_state['bravais'] = None
    if 'peak_name' not in st.session_state:
        st.session_state['peak_name'] = None
    if 'result' not in st.session_state:
        st.session_state['result'] = None
    if 'peakDf_indexing' not in st.session_state:
        st.session_state['peakDf_indexing'] = None
    if 'selected_candidates' not in st.session_state:
        st.session_state['selected_candidates'] = None
    if 'list_candidates' not in st.session_state:
        st.session_state['list_candidates'] = None
    if 'names_candidate' not in st.session_state:
        st.session_state['names_candidate'] = None

    if 'menu_status' not in st.session_state:
        st.session_state['complete_jobs'] = None
    if 'menu_upload' not in st.session_state:
        st.session_state['menu_upload'] = None
    if 'menu_peaksearch' not in st.session_state:
        st.session_state['menu_peaksearch'] = None
    if 'menu_indexing' not in st.session_state:
        st.session_state['menu_indexing'] = None
    if 'uploded_param' not in st.session_state:
        st.session_state['uploaded_param'] = None
    if 'uploaded_hist' not in st.session_state:
        st.session_state['uploaded_hist'] = None
    if 'candidate_exist' not in st.session_state:
        st.session_state['candidate_exist'] = None
    
#setup_session_state ()