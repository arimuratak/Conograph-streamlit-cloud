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

    if 'mess_idx' not in st.session_state:
        st.session_state['mess_idx'] = None
    if 'params_idx' not in st.session_state:
        st.session_state['params_cono'] = None
    if 'params_idx_defau' not in st.session_state:
        st.session_state['params_idx_defau'] = None
    if 'bravais' not in st.session_state:
        st.session_state['bravais'] = None