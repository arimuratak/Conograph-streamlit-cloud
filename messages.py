messages = {
    'eng' : {
        'main_title' : 'Conograph\n(Peak Search & Indexing)',
        'down_menu_1' : {
            'main' : 'File',
            'menu_1' : 'New Project...',
            'menu_2' : 'Open Project..',
            'menu_3' : 'References..',
            'menu_4' : 'Exit..'
            }, 
        'down_menu_2' :{
            'main' : 'Run',
            'menu_1' : 'Run peaksearch',
            'menu_2' : 'Run auto-indexing',
            'menu_3' : 'Refine & Store'},
        
        'down_menu_3' : {
            'main': 'Help',
            'menu_1' : 'Manual...',
            'menu_2' : 'About Conograph...',
            'menu_3' : 'Language'},

        'peaksearch' : {
            'main' : 'Peaksearch',
            'param' : 'Peak search parameters',
            'smth_mes' : 'Number of data points & area for smooting',
            'tbl_col1' : 'Number of Poins',
            'tbl_col2' : 'End of area',
            'fix_param' : 'fix',
            'tbl_add' : 'add',
            'tbl_del' : 'delete',
            'area_mes' : 'PeakSearch area',
            'th_mes' : 'Lower threshold for peak-heights',
            'th_sel_1' : 'use c x error',
            'th_sel_2' : 'use this c',
            'delpk_mes' : 'Remove Kα2 peaks ?',
            'exec_sel_1' : 'Yes',
            'exec_sel_2' : 'No',
            'wavelen_mes' : 'wave length (A) element / kα1 / kα2',
            'wavelen_sel' : 'select'},

        'graph' : {
            'diffPattern' : 'Diffraction pattern',
            'err' : 'Error',
            'smthCuv' : 'Smoothed curve',
            'peakPos' : 'Peak Position',
            'pos' : 'Position',
            'peakH' : 'Peak height',
            'fwhm' : 'FWHM',
            'sel' : 'Use for indexing',
            'pks_result' : 'Peak search result',
            'bestM' : 'Best M',
            'latticeConst' : 'Lattice constants',
            'log' : 'Log'
        },

        'indexing' : {
            'main' : 'Indexing',
            'param' : 'Indexing parameters',
            
            'level' : 'Search level',
            'quickSearch' : 'Quick search',
            'deepSearch' : 'Exhaustive search',
            'nPeak' : 'Num peak points used in search',

            'select' : 'Method selection',
            'tof' : 'TOF',
            'angleDisp' : 'Angle dispersion',
            'convParam' : 'Conversion parameter',
            'waveLen' : 'Wave length (Å)',
            'zeroPoint' : 'Zero point shift : Δ2θ',
            'nPeakForM' : 'Number of peaks for FOM',
            'minMaxPeak' : 'Lower & Upper thresholds for number of compted lines between 1st and 20th observed lines',
            'minFOM' : 'Figure of merit M: min',
            'rangeLattice' : 'Min & Max of lattice constatnt',
            'resolution' : 'Relative error tolerance for duplicated solutions',
            
            'tric' : 'Triclinic',
            'monoc_P' : 'Monoclinic (P)',
            'monoc_A' : 'Monoclinic (A)',
            'monoc_B' : 'Monoclinic (B)',
            'monoc_C' : 'Monoclinic (C)',
            'ortho_P' : 'Orthorhombic (P)',
            'ortho_C' : 'Orthorhombic (C)',
            'ortho_I' : 'Orthorhombic (I)',
            'ortho_F' : 'Orthorhombic (F)',
            'tetra_P' : 'Tetragonal (P)',
            'tetra_I' : 'Tetragonal (I)',
            'rhombo' : 'Rhombohedral',
            'hexago' : 'Hexagonal',
            'cubic_P' : 'Cubic (P)',
            'cubic_I' : 'Cubic (I)',
            'cubic_F' : 'Cubic (F)',

            'threshPrim' : 'Volume of primitive cell (Å)',
            'maxNumZone' : 'Number of zones used for serach',
            'v4linearSum' : 'Torelance level of errors of sums of q-values',
            'numPrimCell' : 'Max number of enumerated primitive cells',
            'minMwu' : 'Min value of Mwu',
            'minMrev' : 'Min value of Mrev',
            'minDistPoints' : 'Min distance between lattice points',
            'maxLatticeConst' : 'Max value of lattice constatnts'


            }
    },

    'jpn' : {
        'main_title' : 'Conograph\n(ピークサーチ & Indexing)',
        'down_menu_1' : {
            'main' : 'ファイル',
            'menu_1' : '新しいプロジェクト',
            'menu_2' : 'プロジェクト開く',
            'menu_3' : '環境設定',
            'menu_4' : '終了'},
        'down_menu_2' :{
            'main' : '実行',
            'menu_1' : 'ピークサーチを実行',
            'menu_2' : '指数付けを実行',
            'menu_3' : '細密化して実行'},
        
        'down_menu_3' : {
            'main': 'Help',
            'menu_1' : 'マニュアル',
            'menu_2' : 'Conographについて...',
            'menu_3' : 'Language'},

        'peaksearch' : {
            'main' : 'ピークサーチ',
            'param' : 'ピークサーチパラメータ',
            'smth_mes' : '1点の平滑化に用いるデータ点数と範囲の設定',
            'tbl_col1' : 'データ点数',
            'tbl_col2' : '区間の終値',
            'fix_param' : '確定',
            'tbl_add' : '追加',
            'tbl_del' : '削除',
            'area_mes' : 'ピークサーチエリア',
            'th_mes' : 'ピーク高さの下限しきい値の考え方',
            'th_sel_1' : '強度エラー値のc倍',
            'th_sel_2' : '固定値c',
            'delpk_mes' : 'kα2ピーク除去(特性X線)',
            'exec_sel_1' : '行う',
            'exec_sel_2' : '行わない',
            'wavelen_mes' : '波長(A): 元素 / kα1 / kα2',
            'wavelen_sel' : '選択'
            },
        
        'graph' : {
            'diffPattern' : '回折パターン',
            'err' : '誤差',
            'smthCuv' : '平滑化曲線',
            'peakPos' : 'ピーク位置',
            'pos' : '位置',
            'peakH' : 'ピーク高さ',
            'fwhm' : '半値幅',
            'sel' : '指標付けに使用',
            'pks_result' : 'ピークサーチ結果',
            'bestM' : 'Best M',
            'latticeConst' : '格子定数',
            'log' : 'ログ表表示'
        },

        'indexing' : {
            'main' : '指数付け',
            'param' : '指標付けパラメータ',
            
            'level' : '探索レベル',
            'quickSearch' : '高速探索',
            'deepSearch' : '丁寧探索',
            'nPeak' : '探索に使用するピーク数',

            'select' : '方法の選択',
            'tof' : '飛行時間法',
            'angleDisp' : '角度分散法',
            'convParam' : 'コンバージョンパラメータ',
            'waveLen' : '波長 (Å)',
            'zeroPoint' : 'ゼロ点シフト : Δ2θ',
            'nPeakForM' : '指数 Mの計算に使用するピーク数',
            'minMaxPeak' : '1本目から20本目までのピーク（観測値）の間に存在するピーク（計算値）の最小数と最大数',
            'minFOM' : '指数 Mの最小値：',
            'rangeLattice' : '格子定数の最小・最大値',
            'resolution' : '重複した解を探索する際の許容相対誤差',

            'tric' : '三斜晶',
            'monoc_P' : '単斜晶 (P)',
            'monoc_A' : '単斜晶 (A)',
            'monoc_B' : '単斜晶 (B)',
            'monoc_C' : '単斜晶 (C)',
            'ortho_P' : '斜方晶 (P)',
            'ortho_C' : '斜方晶 (C)',
            'ortho_I' : '斜方晶 (I)',
            'ortho_F' : '斜方晶 (F)',
            'tetra_P' : '正方晶 (P)',
            'tetra_I' : '正方晶 (I)',
            'rhombo' : '三方晶',
            'hexago' : '六方晶',
            'cubic_P' : '立方晶 (P)',
            'cubic_I' : '立方晶 (I)',
            'cubic_F' : '立方晶 (F)',

            'threshPrim' : 'Primitive cell体積の範囲 (Å)',
            'maxNumZone' : '探索に使用するzoneの最大数',
            'v4linearSum' : 'q値の線形和における誤差の許容レベル',
            'numPrimCell' : '取得するPrimitive cellの数',
            'minMwu' : 'Mwu の最小値',
            'minMrev' : 'Mrev の最小値',
            'minDistPoints' : '格子点間距離のしきい値',
            'maxLatticeConst' : '各ブラベー格子について取得する格子定数の最大数'


        }
    }
}