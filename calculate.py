import numpy as np
import pandas as pd


def calculate_moora(df, criteria_type, weights):
    """
    Menghitung nilai MOORA dengan normalisasi dan pembobotan.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame yang berisi data alternatif dengan kolom 'Name' dan kriteria lainnya
    criteria_type : dict
        Dictionary yang menentukan tipe setiap kriteria ('benefit' atau 'cost')
        Contoh: {'Price': 'cost', 'Distance': 'cost', 'Size': 'benefit'}
    weights : dict
        Dictionary bobot untuk setiap kriteria dalam bentuk desimal (total = 1.0)
        Contoh: {'Price': 0.3, 'Distance': 0.25, 'Size': 0.15}
    
    Returns:
    --------
    tuple
        (normalized_matrix, weighted_normalized_matrix, yi_values)
        - normalized_matrix: numpy.ndarray - Matrix ternormalisasi
        - weighted_normalized_matrix: numpy.ndarray - Matrix ternormalisasi terbobot
        - yi_values: numpy.ndarray - Nilai Yi untuk setiap alternatif
    
    Raises:
    -------
    ValueError
        - Jika dataset kosong
        - Jika tidak ada kriteria selain kolom 'Name'
        - Jika ada nilai nol atau negatif dalam dataset
    
    Examples:
    ---------
    >>> df = pd.DataFrame({
    ...     'Name': ['Kost_A', 'Kost_B'],
    ...     'Price': [1800, 900],
    ...     'Distance': [2.5, 1.0]
    ... })
    >>> criteria_type = {'Price': 'cost', 'Distance': 'cost'}
    >>> weights = {'Price': 0.5, 'Distance': 0.5}
    >>> normalized, weighted, yi = calculate_moora(df, criteria_type, weights)
    """
    
    # Validasi 1: Dataset tidak boleh kosong
    if df.empty:
        raise ValueError("Dataset tidak boleh kosong!")
    
    # Ambil kolom kriteria (semua kecuali Name)
    criteria_cols = [col for col in df.columns if col != 'Name']
    
    # Validasi 2: Harus ada minimal 1 kriteria
    if not criteria_cols:
        raise ValueError("Dataset harus memiliki minimal 1 kriteria selain kolom Name!")
    
    # Validasi 3: Semua nilai numerik harus positif (tidak boleh nol atau negatif)
    for col in criteria_cols:
        if (df[col] <= 0).any():
            raise ValueError(f"Kolom '{col}' mengandung nilai nol atau negatif! Semua nilai harus positif.")
    
    # Matrix keputusan (X)
    X = df[criteria_cols].values
    
    # Langkah 1: Normalisasi matrix
    # Rumus: xij / √(Σxij²)
    normalized = np.zeros_like(X, dtype=float)
    for j in range(X.shape[1]):
        denominator = np.sqrt(np.sum(X[:, j] ** 2))
        normalized[:, j] = X[:, j] / denominator
    
    # Langkah 2: Kalikan dengan bobot
    # Matrix terbobot = Matrix ternormalisasi × Bobot
    weighted_normalized = np.zeros_like(normalized)
    for j, col in enumerate(criteria_cols):
        weighted_normalized[:, j] = normalized[:, j] * weights[col]
    
    # Langkah 3: Optimasi atribut
    # Pisahkan indeks kriteria benefit dan cost
    benefit_indices = [i for i, col in enumerate(criteria_cols) if criteria_type[col] == 'benefit']
    cost_indices = [i for i, col in enumerate(criteria_cols) if criteria_type[col] == 'cost']
    
    # Langkah 4: Hitung Yi = Σ(benefit × bobot) - Σ(cost × bobot)
    yi_values = np.zeros(X.shape[0])
    
    # Sum benefit criteria
    if benefit_indices:
        yi_values += np.sum(weighted_normalized[:, benefit_indices], axis=1)
    
    # Subtract cost criteria
    if cost_indices:
        yi_values -= np.sum(weighted_normalized[:, cost_indices], axis=1)
    
    return normalized, weighted_normalized, yi_values


def validate_weights(weights):
    """
    Validasi bahwa total bobot = 1.0 (100%)
    
    Parameters:
    -----------
    weights : dict
        Dictionary bobot untuk setiap kriteria
    
    Returns:
    --------
    bool
        True jika valid, False jika tidak
    
    Examples:
    ---------
    >>> weights = {'Price': 0.3, 'Distance': 0.3, 'Size': 0.4}
    >>> validate_weights(weights)
    True
    """
    total = sum(weights.values())
    return abs(total - 1.0) < 0.0001  # Toleransi floating point


def validate_criteria_type(criteria_type):
    """
    Validasi bahwa semua tipe kriteria adalah 'benefit' atau 'cost'
    
    Parameters:
    -----------
    criteria_type : dict
        Dictionary tipe kriteria
    
    Returns:
    --------
    bool
        True jika valid, False jika tidak
    
    Examples:
    ---------
    >>> criteria_type = {'Price': 'cost', 'Size': 'benefit'}
    >>> validate_criteria_type(criteria_type)
    True
    """
    valid_types = ['benefit', 'cost']
    return all(ctype in valid_types for ctype in criteria_type.values())


def create_result_dataframe(df, yi_values):
    """
    Membuat DataFrame hasil dengan Yi Score dan Ranking
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame original
    yi_values : numpy.ndarray
        Array nilai Yi
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame hasil dengan kolom tambahan Yi (Score) dan Ranking
    
    Examples:
    ---------
    >>> df = pd.DataFrame({'Name': ['A', 'B'], 'Price': [100, 200]})
    >>> yi_values = np.array([0.5, 0.3])
    >>> result = create_result_dataframe(df, yi_values)
    >>> result.columns.tolist()
    ['Name', 'Price', 'Yi (Score)', 'Ranking']
    """
    result_df = df.copy()
    result_df['Yi (Score)'] = yi_values
    result_df['Ranking'] = result_df['Yi (Score)'].rank(ascending=False, method='min').astype(int)
    result_df = result_df.sort_values('Ranking')
    return result_df
