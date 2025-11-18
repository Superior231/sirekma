import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Import fungsi dari calculate.py
from calculate import calculate_moora, validate_weights, validate_criteria_type, create_result_dataframe


class TestCalculateMoora(unittest.TestCase):
    """Test suite untuk fungsi calculate_moora"""
    
    def setUp(self):
        """Setup data test yang akan digunakan di setiap test case"""
        # Sample dataset
        self.df = pd.DataFrame({
            'Name': ['Kost_A', 'Kost_B', 'Kost_C'],
            'Price': [1800, 900, 2000],
            'Distance': [2.5, 1.0, 3.5],
            'Size': [15, 12, 18],
            'Wifi': [50, 100, 75],
            'Security_Score': [8, 9, 7]
        })
        
        # Criteria type (benefit/cost)
        self.criteria_type = {
            'Price': 'cost',
            'Distance': 'cost',
            'Size': 'benefit',
            'Wifi': 'benefit',
            'Security_Score': 'benefit'
        }
        
        # Equal weights (20% each)
        self.weights_equal = {
            'Price': 0.20,
            'Distance': 0.20,
            'Size': 0.20,
            'Wifi': 0.20,
            'Security_Score': 0.20
        }
        
        # Custom weights
        self.weights_custom = {
            'Price': 0.30,
            'Distance': 0.25,
            'Size': 0.15,
            'Wifi': 0.15,
            'Security_Score': 0.15
        }
    
    def test_normalization_sum_of_squares(self):
        """Test: Sum of squares untuk setiap kolom ternormalisasi harus = 1"""
        normalized, _, _ = calculate_moora(
            self.df, self.criteria_type, self.weights_equal
        )
        
        for j in range(normalized.shape[1]):
            sum_squares = np.sum(normalized[:, j] ** 2)
            self.assertAlmostEqual(sum_squares, 1.0, places=10,
                                 msg=f"Sum of squares untuk kolom {j} tidak sama dengan 1")
    
    def test_normalized_matrix_shape(self):
        """Test: Shape matrix ternormalisasi harus sama dengan input"""
        normalized, _, _ = calculate_moora(
            self.df, self.criteria_type, self.weights_equal
        )
        
        expected_shape = (3, 5)  # 3 rows, 5 criteria columns
        self.assertEqual(normalized.shape, expected_shape,
                        "Shape matrix ternormalisasi tidak sesuai")
    
    def test_weighted_matrix_shape(self):
        """Test: Shape matrix terbobot harus sama dengan matrix ternormalisasi"""
        normalized, weighted, _ = calculate_moora(
            self.df, self.criteria_type, self.weights_equal
        )
        
        self.assertEqual(weighted.shape, normalized.shape,
                        "Shape matrix terbobot tidak sesuai dengan normalized")
    
    def test_yi_values_length(self):
        """Test: Jumlah Yi values harus sama dengan jumlah alternatif"""
        _, _, yi_values = calculate_moora(
            self.df, self.criteria_type, self.weights_equal
        )
        
        self.assertEqual(len(yi_values), len(self.df),
                        "Jumlah Yi values tidak sesuai dengan jumlah alternatif")
    
    def test_weighted_calculation(self):
        """Test: Matrix terbobot = normalized × weight"""
        normalized, weighted, _ = calculate_moora(
            self.df, self.criteria_type, self.weights_equal
        )
        
        criteria_cols = [col for col in self.df.columns if col != 'Name']
        for j, col in enumerate(criteria_cols):
            expected_weighted = normalized[:, j] * self.weights_equal[col]
            np.testing.assert_array_almost_equal(
                weighted[:, j], expected_weighted,
                err_msg=f"Weighted calculation salah untuk kolom {col}"
            )
    
    def test_different_weights_produce_different_results(self):
        """Test: Bobot berbeda menghasilkan Yi values berbeda"""
        _, _, yi_equal = calculate_moora(
            self.df, self.criteria_type, self.weights_equal
        )
        _, _, yi_custom = calculate_moora(
            self.df, self.criteria_type, self.weights_custom
        )
        
        self.assertFalse(np.array_equal(yi_equal, yi_custom),
                        "Bobot berbeda tidak menghasilkan Yi values berbeda")
    
    def test_all_benefit_criteria(self):
        """Test: Semua kriteria benefit"""
        all_benefit = {col: 'benefit' for col in self.criteria_type.keys()}
        
        _, _, yi_values = calculate_moora(
            self.df, all_benefit, self.weights_equal
        )
        
        # Semua Yi values harus positif untuk all benefit
        self.assertTrue(all(yi >= 0 for yi in yi_values),
                       "Dengan all benefit, seharusnya tidak ada Yi negatif")
    
    def test_all_cost_criteria(self):
        """Test: Semua kriteria cost"""
        all_cost = {col: 'cost' for col in self.criteria_type.keys()}
        
        _, _, yi_values = calculate_moora(
            self.df, all_cost, self.weights_equal
        )
        
        # Semua Yi values harus negatif atau nol untuk all cost
        self.assertTrue(all(yi <= 0 for yi in yi_values),
                       "Dengan all cost, seharusnya tidak ada Yi positif")
    
    def test_normalization_preserves_ratios(self):
        """Test: Normalisasi mempertahankan rasio relatif"""
        criteria_cols = [col for col in self.df.columns if col != 'Name']
        X = self.df[criteria_cols].values
        
        normalized, _, _ = calculate_moora(
            self.df, self.criteria_type, self.weights_equal
        )
        
        # Untuk setiap kolom, cek apakah rasio terbesar/terkecil konsisten
        for j in range(X.shape[1]):
            original_ratio = np.max(X[:, j]) / np.min(X[:, j])
            normalized_ratio = np.max(normalized[:, j]) / np.min(normalized[:, j])
            
            self.assertAlmostEqual(original_ratio, normalized_ratio, places=5,
                                 msg=f"Rasio tidak konsisten untuk kolom {j}")
    
    def test_zero_weight_has_no_effect(self):
        """Test: Bobot nol membuat kriteria tidak berpengaruh"""
        weights_zero_price = self.weights_equal.copy()
        weights_zero_price['Price'] = 0.0
        weights_zero_price['Distance'] = 0.25  # Adjust untuk total = 1
        
        # Ubah harga drastis
        df_modified = self.df.copy()
        df_modified['Price'] = [10000, 10000, 10000]
        
        _, _, yi_original = calculate_moora(
            self.df, self.criteria_type, weights_zero_price
        )
        _, _, yi_modified = calculate_moora(
            df_modified, self.criteria_type, weights_zero_price
        )
        
        # Yi values harus sama karena Price weight = 0
        np.testing.assert_array_almost_equal(
            yi_original, yi_modified,
            err_msg="Zero weight seharusnya membuat kriteria tidak berpengaruh"
        )
    
    def test_ranking_consistency(self):
        """Test: Alternatif dengan nilai lebih baik mendapat Yi lebih tinggi"""
        # Buat dataset dengan alternatif yang jelas lebih baik
        df_clear = pd.DataFrame({
            'Name': ['Best', 'Worst'],
            'Price': [500, 5000],      # Best lebih murah (cost)
            'Distance': [0.5, 10.0],   # Best lebih dekat (cost)
            'Size': [25, 10],          # Best lebih besar (benefit)
            'Wifi': [100, 10],         # Best lebih cepat (benefit)
            'Security_Score': [10, 1]  # Best lebih aman (benefit)
        })
        
        _, _, yi_values = calculate_moora(
            df_clear, self.criteria_type, self.weights_equal
        )
        
        self.assertGreater(yi_values[0], yi_values[1],
                          "Alternatif terbaik harus memiliki Yi lebih tinggi")
    
    def test_empty_dataframe(self):
        """Test: Handling empty dataframe"""
        df_empty = pd.DataFrame({
            'Name': [],
            'Price': [],
            'Distance': [],
            'Size': [],
            'Wifi': [],
            'Security_Score': []
        })
        
        # Empty dataframe harus raise ValueError
        with self.assertRaises(ValueError) as context:
            calculate_moora(df_empty, self.criteria_type, self.weights_equal)
        
        self.assertIn("tidak boleh kosong", str(context.exception).lower())

    def test_criteria_cols(self):
        """Test: Dataset harus memiliki minimal 1 kriteria selain kolom Name"""
        df_no_criteria = pd.DataFrame({
            'Name': ['A', 'B', 'C']
        })

        # criteria_type dan weights tidak relevan karena harus error sebelum dipakai
        criteria_type = {}
        weights = {}

        with self.assertRaises(ValueError) as context:
            calculate_moora(df_no_criteria, criteria_type, weights)

        self.assertIn("Dataset harus memiliki minimal 1 kriteria selain kolom Name!", str(context.exception).lower())

    
    def test_negative_values_in_dataset(self):
        """Test: Dataset dengan nilai negatif harus raise error"""
        df_negative = pd.DataFrame({
            'Name': ['Kost_A', 'Kost_B'],
            'Price': [1800, -900],  # Nilai negatif
            'Distance': [2.5, 1.0],
            'Size': [15, 12],
            'Wifi': [50, 100],
            'Security_Score': [8, 9]
        })
        
        with self.assertRaises(ValueError) as context:
            calculate_moora(df_negative, self.criteria_type, self.weights_equal)
        
        self.assertIn("negatif", str(context.exception).lower())
    
    def test_zero_values_in_dataset(self):
        """Test: Dataset dengan nilai nol harus raise error"""
        df_zero = pd.DataFrame({
            'Name': ['Kost_A', 'Kost_B'],
            'Price': [1800, 900],
            'Distance': [0, 1.0],  # Nilai nol
            'Size': [15, 12],
            'Wifi': [50, 100],
            'Security_Score': [8, 9]
        })
        
        with self.assertRaises(ValueError) as context:
            calculate_moora(df_zero, self.criteria_type, self.weights_equal)
        
        self.assertIn("nol", str(context.exception).lower())
    
    def test_single_alternative(self):
        """Test: Single alternative"""
        df_single = self.df.iloc[[0]].copy()
        
        normalized, weighted, yi_values = calculate_moora(
            df_single, self.criteria_type, self.weights_equal
        )
        
        self.assertEqual(len(yi_values), 1,
                        "Single alternative harus menghasilkan 1 Yi value")
        # Normalized values untuk single row harus = 1.0 (karena √(x²) = |x|)
        self.assertTrue(all(abs(normalized[0, j]) == 1.0 for j in range(normalized.shape[1])),
                       "Normalized values untuk single alternative harus = ±1.0")


class TestDataValidation(unittest.TestCase):
    """Test suite untuk validasi data input"""
    
    def test_weight_sum_validation(self):
        """Test: Validasi total bobot = 1.0"""
        weights = {
            'Price': 0.30,
            'Distance': 0.25,
            'Size': 0.15,
            'Wifi': 0.15,
            'Security_Score': 0.15
        }
        
        self.assertTrue(validate_weights(weights),
                       "Total bobot harus = 1.0")
    
    def test_weight_sum_validation_invalid(self):
        """Test: Validasi total bobot tidak = 1.0"""
        weights = {
            'Price': 0.30,
            'Distance': 0.25,
            'Size': 0.15,
            'Wifi': 0.15,
            'Security_Score': 0.20  # Total = 1.05
        }
        
        self.assertFalse(validate_weights(weights),
                        "Total bobot tidak = 1.0 harus invalid")
    
    def test_criteria_type_validation(self):
        """Test: Criteria type harus benefit atau cost"""
        criteria_type = {
            'Price': 'cost',
            'Distance': 'cost',
            'Size': 'benefit',
            'Wifi': 'benefit',
            'Security_Score': 'benefit'
        }
        
        self.assertTrue(validate_criteria_type(criteria_type),
                       "Criteria type valid harus return True")
    
    def test_criteria_type_validation_invalid(self):
        """Test: Criteria type invalid"""
        criteria_type = {
            'Price': 'cost',
            'Distance': 'invalid',  # Type invalid
            'Size': 'benefit'
        }
        
        self.assertFalse(validate_criteria_type(criteria_type),
                        "Criteria type invalid harus return False")
    
    def test_positive_values_in_dataset(self):
        """Test: Semua nilai numerik harus positif"""
        df = pd.DataFrame({
            'Name': ['Kost_A', 'Kost_B'],
            'Price': [1800, 900],
            'Distance': [2.5, 1.0],
            'Size': [15, 12],
            'Wifi': [50, 100],
            'Security_Score': [8, 9]
        })
        
        criteria_cols = [col for col in df.columns if col != 'Name']
        for col in criteria_cols:
            self.assertTrue(all(df[col] > 0),
                          f"Kolom {col} harus memiliki nilai positif")


class TestEdgeCases(unittest.TestCase):
    """Test suite untuk edge cases"""
    
    def setUp(self):
        """Setup data test"""
        self.criteria_type = {
            'Price': 'cost',
            'Distance': 'cost',
            'Size': 'benefit',
            'Wifi': 'benefit',
            'Security_Score': 'benefit'
        }
        
        self.weights_equal = {
            'Price': 0.20,
            'Distance': 0.20,
            'Size': 0.20,
            'Wifi': 0.20,
            'Security_Score': 0.20
        }
    
    def test_identical_alternatives(self):
        """Test: Alternatif identik harus mendapat Yi yang sama"""
        df = pd.DataFrame({
            'Name': ['Kost_A', 'Kost_B', 'Kost_C'],
            'Price': [1000, 1000, 1000],
            'Distance': [2.0, 2.0, 2.0],
            'Size': [15, 15, 15],
            'Wifi': [50, 50, 50],
            'Security_Score': [8, 8, 8]
        })
        
        _, _, yi_values = calculate_moora(df, self.criteria_type, self.weights_equal)
        
        # Semua Yi values harus sama
        self.assertTrue(all(abs(yi - yi_values[0]) < 1e-10 for yi in yi_values),
                       "Alternatif identik harus memiliki Yi yang sama")
    
    def test_extreme_weight_distribution(self):
        """Test: Bobot ekstrem (hampir semua di satu kriteria)"""
        weights = {
            'Price': 0.96,
            'Distance': 0.01,
            'Size': 0.01,
            'Wifi': 0.01,
            'Security_Score': 0.01
        }
        
        self.assertTrue(validate_weights(weights),
                       "Total bobot ekstrem harus tetap = 1.0")


class TestResultInterpretation(unittest.TestCase):
    """Test suite untuk interpretasi hasil"""
    
    def test_create_result_dataframe(self):
        """Test: Fungsi create_result_dataframe"""
        df = pd.DataFrame({
            'Name': ['Kost_A', 'Kost_B', 'Kost_C'],
            'Price': [1800, 900, 2000]
        })
        yi_values = np.array([0.15, 0.25, 0.10])
        
        result_df = create_result_dataframe(df, yi_values)
        
        # Cek kolom yang ada
        self.assertIn('Yi (Score)', result_df.columns,
                     "Result harus memiliki kolom Yi (Score)")
        self.assertIn('Ranking', result_df.columns,
                     "Result harus memiliki kolom Ranking")
        
        # Cek ranking
        self.assertEqual(result_df.iloc[0]['Ranking'], 1,
                        "Ranking tertinggi harus = 1")
    
    def test_ranking_order(self):
        """Test: Ranking harus descending berdasarkan Yi"""
        df = pd.DataFrame({
            'Name': ['Kost_A', 'Kost_B', 'Kost_C'],
            'Price': [1800, 900, 2000]
        })
        yi_values = np.array([0.15, 0.25, 0.10])
        
        result_df = create_result_dataframe(df, yi_values)
        
        # Cek apakah Yi Score descending
        yi_scores = result_df['Yi (Score)'].tolist()
        self.assertEqual(yi_scores, sorted(yi_scores, reverse=True),
                        "Ranking harus descending berdasarkan Yi Score")


if __name__ == '__main__':
    # Run tests dengan verbosity
    unittest.main(verbosity=2)
