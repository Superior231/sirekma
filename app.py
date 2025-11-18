import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Import fungsi dari calculate.py
from calculate import calculate_moora, validate_weights, create_result_dataframe


# Konfigurasi halaman
st.set_page_config(page_title="SIREKMA: Sistem Rekomendasi Kost Mahasiswa", layout="wide")
st.markdown("""
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .bg-primary {
            background-color: #FF4B4B !important;
        }
        .text-primary {
            color: #FF4B4B !important;
        }
        .stAlertContainer ul {
            list-style-type: none !important;
            padding-left: 0 !important;
        }
        .stAlertContainer ul li {
            margin-left: 5px !important;
        }

        [data-testid="stSidebar"] a {
            text-decoration: none !important;
            color: var(--text-color);
            text-align: center !important;
            opacity: 0.7;
        }
        [data-testid="stSidebar"] a:hover {
            text-decoration: none !important;
            color: #FF4B4B !important;
            opacity: 1;
        }

        .footer {
            opacity: 0.7;
            color: var(--text-color);
        }
        .footer a {
            text-decoration: none !important;
            color: var(--text-color);
        }
        .footer a:hover {
            text-decoration: underline !important;
            color: #FF4B4B !important;
        }
    </style>
""", unsafe_allow_html=True)


# Judul dan deskripsi aplikasi
st.title("SIREKMA: Sistem Rekomendasi Kost Mahasiswa")
st.markdown("""
            **SIREKMA (Sistem Rekomendasi Kost Mahasiswa)** merupakan sistem rekomendasi berbasis Python dengan antarmuka interaktif menggunakan Streamlit yang dirancang untuk membantu mahasiswa dalam memilih kost terbaik sesuai kebutuhan dan preferensi mereka. Sistem ini menggunakan metode MOORA (Multi-Objective Optimization on the basis of Ratio Analysis) untuk menilai dan memberikan peringkat rekomendasi kost secara objektif dan transparan.

            Dataset yang digunakan dalam SIREKMA berisi beberapa variabel penting yang menjadi faktor pertimbangan utama dalam memilih tempat kost, yaitu:
            <table>
                <tr>
                    <th class="bg-primary">Kriteria</th>
                    <th class="bg-primary">Satuan</th>
                    <th class="bg-primary text">Deskripsi</th>
                </tr>
                <tr>
                    <td>Name</td>
                    <td>String</td>
                    <td>Nama atau identitas kost.</td>
                </tr>
                <tr>
                    <td>Price</td>
                    <td>IDR</td>
                    <td>Harga sewa kost per bulan.</td>
                </tr>
                <tr>
                    <td>Distance</td>
                    <td>km</td>
                    <td>Jarak kost dari kampus atau lokasi tujuan utama mahasiswa.</td>
                </tr>
                <tr>
                    <td>Size</td>
                    <td>m²</td>
                    <td>Ukuran atau luas kamar kost.</td>
                </tr>
                <tr>
                    <td>WiFi</td>
                    <td>Mbps</td>
                    <td>Ketersediaan fasilitas internet WiFi.</td>
                </tr>
                <tr>
                    <td>Security Score</td>
                    <td>0-10</td>
                    <td>Skor keamanan lingkungan kost.</td>
                </tr>
            </table>

            Melalui proses perhitungan berbasis algoritma pemeringkatan (ranking) dengan menggunakan MOORA, SIREKMA menghasilkan daftar rekomendasi kost terbaik dengan urutan prioritas berdasarkan kombinasi variabel tersebut. Hasil rekomendasi ditampilkan secara real-time dalam antarmuka Streamlit yang sederhana dan mudah dipahami. Selain itu, sistem menyediakan fitur unduh hasil rekomendasi dalam format .CSV, sehingga pengguna dapat menyimpan dan menganalisis data secara mandiri di luar aplikasi.
             
            Dengan SIREKMA, mahasiswa dapat mengambil keputusan lebih cepat, akurat, dan efisien dalam memilih kost yang paling sesuai dengan kebutuhan, preferensi, serta kondisi finansial mereka.
            """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
            ## <i class='bx bxs-info-circle fs-3'></i> Tentang MOORA
            
            **MOORA (Multi-Objective Optimization on the basis of Ratio Analysis)** adalah metode yang digunakan untuk 
            mengoptimalkan dua atau lebih atribut yang saling bertentangan secara bersamaan.
            
            **Langkah-langkah MOORA dengan Bobot:**
            1. **Normalisasi Matrix** - Setiap nilai kriteria dinormalisasi dengang menggunakan rumus: xij / √(Σxij²)
            2. **Pembobotan** - Nilai ternormalisasi dikalikan dengan bobot kriteria
            3. **Optimasi Atribut** - Kriteria dibagi menjadi benefit dan cost
            4. **Perhitungan Yi** - Yi = Σ(benefit × bobot) - Σ(cost × bobot)
            5. **Ranking** - Alternatif diurutkan berdasarkan nilai Yi (tertinggi = terbaik)
            
            **Fitur Bobot:**
            - Input manual bobot untuk setiap kriteria
            - Validasi bobot harus total = 100%
            - Preset bobot (Equal, Recommended, Custom)
            - Slider interaktif untuk adjust bobot
            
            **Kelebihan MOORA:**
            - Sederhana dan mudah dipahami
            - Perhitungan cepat dan efisien
            - Fleksibel untuk berbagai kriteria
            - Hasil objektif dan konsisten
            - Dapat disesuaikan dengan preferensi pengguna
            """, unsafe_allow_html=True)

st.markdown("---")

st.header("📁 Upload Dataset")
uploaded_file = st.file_uploader("Upload file CSV", type=['csv'])


# Sidebar
st.sidebar.header("🏠 SIREKMA")
basic_menu = {
    "<i class='bx bxs-home'></i> <span>Home</span>": "#sirekma-sistem-rekomendasi-kost-mahasiswa",
    "<i class='bx bxs-info-circle'></i> Tentang MOORA": "#tentang-moora",
    "<i class='bx bxs-cloud-upload'></i> Upload Dataset": "#upload-dataset",
}
advanced_menu = {
    "<i class='bx bxs-cog'></i> Pengaturan Kriteria": "#pengaturan-kriteria",
    "<i class='bx bxs-bar-chart-alt-2'></i> Hasil Perhitungan": "#hasil-perhitungan-moora",
    "<i class='bx bxs-download'></i> Download Hasil": "#download-hasil",
}

# Basic menu
for label, anchor in basic_menu.items():
    st.sidebar.markdown(f"[{label}]({anchor})", unsafe_allow_html=True)

# Advanced menu jika file sudah diupload
if uploaded_file is not None:
    for label, anchor in advanced_menu.items():
        st.sidebar.markdown(f"[{label}]({anchor})", unsafe_allow_html=True)


# Main content
if uploaded_file is not None:
    # Baca file CSV
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Dataset berhasil diupload!")
    except pd.errors.EmptyDataError:
        st.error("❌ File CSV kosong atau tidak memiliki kolom!")
        st.stop()
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat membaca file: {e}")
        st.stop()
    
    # Tampilkan dataset
    st.subheader("📊 Dataset Kost Mahasiswa")
    st.dataframe(df, use_container_width=True)
    
    # Informasi dataset
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Jumlah Alternatif", len(df))
    with col2:
        st.metric("Jumlah Kriteria", len(df.columns) - 1)
    with col3:
        st.metric("Total Data Points", df.shape[0] * (df.shape[1] - 1))
    
    st.markdown("---")
    
    # Pengaturan kriteria
    st.subheader("⚙️ Pengaturan Kriteria")
    
    criteria_cols = [col for col in df.columns if col != 'Name']
    
    # Tab untuk pengaturan
    tab_criteria, tab_weights = st.tabs(["📋 Tipe Kriteria", "⚖️ Bobot Kriteria"])
    
    with tab_criteria:
        st.write("Tentukan apakah setiap kriteria termasuk **Benefit** (semakin besar semakin baik) atau **Cost** (semakin kecil semakin baik)")
        
        criteria_type = {}
        cols = st.columns(len(criteria_cols))
        for i, col in enumerate(criteria_cols):
            with cols[i]:
                # Default setting
                default = 'cost' if col in ['Price', 'Distance'] else 'benefit'
                criteria_type[col] = st.selectbox(
                    f"**{col}**",
                    options=['benefit', 'cost'],
                    index=0 if default == 'benefit' else 1,
                    key=f"type_{col}"
                )
    
    with tab_weights:
        st.write("Tentukan bobot kepentingan untuk setiap kriteria")
        
        # Preset bobot
        st.markdown("### 🔥 Preset Bobot")
        preset_option = st.radio(
            "Pilih preset bobot:",
            options=["Equal (Sama Rata)", "Recommended (Rekomendasi)", "Custom (Manual)"],
            horizontal=True
        )
        
        weights = {}
        
        if preset_option == "Equal (Sama Rata)":
            equal_weight = 100 / len(criteria_cols)
            for col in criteria_cols:
                weights[col] = equal_weight
            st.info(f"✓ Setiap kriteria memiliki bobot yang sama: {equal_weight:.2f}%")
            
        elif preset_option == "Recommended (Rekomendasi)":
            # Bobot rekomendasi (sesuaikan dengan kebutuhan)
            recommended = {
                'Price': 30,
                'Distance': 25,
                'Size': 15,
                'Wifi': 15,
                'Security_Score': 15
            }
            for col in criteria_cols:
                weights[col] = recommended.get(col, 100/len(criteria_cols))
            
            st.info("✓ Menggunakan bobot rekomendasi:")
            cols = st.columns(len(criteria_cols))
            for i, col in enumerate(criteria_cols):
                with cols[i]:
                    st.metric(col, f"{weights[col]}%")
        
        else:  # Custom
            st.markdown("### Atur Bobot Manual")
            st.write("Gunakan slider untuk mengatur bobot setiap kriteria (total harus = 100%)")
            
            # Inisialisasi dengan bobot equal
            if 'weights_initialized' not in st.session_state:
                st.session_state.weights_initialized = True
                st.session_state.custom_weights = {col: 100/len(criteria_cols) for col in criteria_cols}
            
            # Slider untuk setiap kriteria
            for col in criteria_cols:
                weights[col] = st.slider(
                    f"**{col}**",
                    min_value=0.0,
                    max_value=100.0,
                    value=st.session_state.custom_weights.get(col, 100/len(criteria_cols)),
                    step=0.5,
                    key=f"weight_{col}",
                    help=f"Bobot kepentingan untuk kriteria {col}"
                )
                st.session_state.custom_weights[col] = weights[col]
        
        # Validasi total bobot
        total_weight = sum(weights.values())
        if abs(total_weight - 100) < 0.01:  # Toleransi kecil untuk floating point
            st.success(f"✅ Total bobot: {total_weight:.2f}%")
        else:
            st.error(f"❌ Total bobot: {total_weight:.2f}% (max 100%)")

        
        # Tampilkan distribusi bobot dalam chart
        if preset_option == "Custom (Manual)":
            st.markdown("### 📊 Distribusi Bobot")
            fig, ax = plt.subplots(figsize=(10, 4))
            colors = plt.cm.Set3(range(len(criteria_cols)))
            ax.bar(criteria_cols, [weights[col] for col in criteria_cols], color=colors)
            ax.set_ylabel('Bobot (%)')
            ax.set_title('Distribusi Bobot Kriteria')
            ax.axhline(y=100/len(criteria_cols), color='r', linestyle='--', label='Equal Weight')
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    
    st.markdown("---")
    
    # Tombol untuk menghitung
    total_weight = sum(weights.values())
    can_calculate = abs(total_weight - 100) < 0.01
    
    if not can_calculate:
        st.warning("⚠️ Total bobot harus = 100% untuk melakukan perhitungan!")
    
    if st.button("Hitung MOORA", type="primary", use_container_width=True, disabled=not can_calculate):
        # Konversi bobot ke desimal (0-1)
        weights_decimal = {k: v/100 for k, v in weights.items()}
        
        try:
            # Hitung MOORA menggunakan fungsi dari calculate.py
            normalized_matrix, weighted_normalized, yi_values = calculate_moora(df, criteria_type, weights_decimal)
            
            # Buat dataframe hasil
            result_df = create_result_dataframe(df, yi_values)
            
            # Tampilkan hasil
            st.markdown("---")
            st.markdown("### 📊 Hasil Perhitungan MOORA")
            
            # Tampilkan bobot yang digunakan
            with st.expander("🔍 Lihat Bobot yang Digunakan"):
                weight_df = pd.DataFrame({
                    'Kriteria': criteria_cols,
                    'Bobot (%)': [weights[col] for col in criteria_cols],
                    'Tipe': [criteria_type[col] for col in criteria_cols]
                })
                st.dataframe(weight_df, use_container_width=True)
            
            # Tab untuk hasil
            tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ranking Akhir", "📋 Matrix Ternormalisasi", "⚖️ Matrix Terbobot", "📊 Visualisasi"])
            
            with tab1:
                st.write("**Hasil Ranking Pemilihan Kost:**")
                
                # Styling untuk top 3
                def highlight_top3(row):
                    color = ''
                    if row['Ranking'] == 1:
                        color = 'background-color: #FFD700; font-weight: bold; color: #000000;'
                    elif row['Ranking'] == 2:
                        color = 'background-color: #C0C0C0; font-weight: bold; color: #000000;'
                    elif row['Ranking'] == 3:
                        color = 'background-color: #CD7F32; font-weight: bold; color: #000000;'
                    return [color] * len(row)
                
                styled_df = result_df.style.apply(highlight_top3, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                # Tampilkan top 3
                st.markdown("### 🥇 Top 3 Rekomendasi Kost")
                top3 = result_df.head(3)
                
                cols = st.columns(3)
                medals = ["🥇", "🥈", "🥉"]
                for i, (idx, row) in enumerate(top3.iterrows()):
                    with cols[i]:
                        st.info(f"""
                        **{medals[i]} Ranking {row['Ranking']}**
                        
                        **{row['Name']}**
                        
                        - 💰 Harga: Rp{row['Price']:,.0f}k
                        - 🚶‍♂️ Jarak: {row['Distance']} km
                        - 📏 Ukuran: {row['Size']} m²
                        - 🛜 WiFi: {row['Wifi']} Mbps
                        - 🛡️ Keamanan: {row['Security_Score']}/10
                        
                        **Yi Score: {row['Yi (Score)']:.4f}**
                        """)
            
            with tab2:
                st.write("**Matrix Keputusan Ternormalisasi:**")
                normalized_df = pd.DataFrame(
                    normalized_matrix,
                    columns=criteria_cols,
                    index=df['Name']
                )
                st.dataframe(normalized_df.style.format("{:.4f}"), use_container_width=True)
                
                st.info("""
                **Catatan:** 
                - Matrix ternormalisasi menggunakan rumus: xij / √(Σxij²)
                - Setiap nilai dinormalisasi terhadap akar kuadrat dari jumlah kuadrat kolom
                """)
            
            with tab3:
                st.write("**Matrix Ternormalisasi Terbobot:**")
                weighted_df = pd.DataFrame(
                    weighted_normalized,
                    columns=criteria_cols,
                    index=df['Name']
                )
                st.dataframe(weighted_df.style.format("{:.4f}"), use_container_width=True)
                
                st.info("""
                **Catatan:** 
                - Matrix terbobot = Matrix ternormalisasi × Bobot kriteria
                - Bobot mempengaruhi kontribusi setiap kriteria terhadap score akhir
                """)
            
            with tab4:
                st.write("**Grafik Perbandingan Yi Score:**")
                chart_data = result_df.set_index('Name')[['Yi (Score)']].sort_values('Yi (Score)', ascending=True)
                st.bar_chart(chart_data)
                st.line_chart(chart_data)
                
                st.write("**Distribusi Kriteria Top 3:**")
                top3_criteria = result_df.head(3).set_index('Name')[criteria_cols]
                st.line_chart(top3_criteria.T)
                
                st.write("**Perbandingan Yi Score Top 3:**")
                top3_yi = result_df.head(3).set_index('Name')[['Yi (Score)']]
                fig, ax = plt.subplots(figsize=(8, 5))
                colors = ['#FFD700', '#C0C0C0', '#CD7F32']
                bars = ax.bar(top3_yi.index, top3_yi['Yi (Score)'].values, color=colors[:len(top3_yi)])
                ax.set_title('Perbandingan Yi Score Top 3')
                ax.set_ylabel('Yi Score')
                ax.set_xlabel('Nama Kost')
                ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
                ax.grid(axis='y', alpha=0.3)
                
                # Label
                for i, (name, score) in enumerate(zip(top3_yi.index, top3_yi['Yi (Score)'].values)):
                    ax.text(i, score, f'{score:.4f}', ha='center', va='bottom' if score > 0 else 'top')
                
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

            
            # Download hasil
            st.markdown("---")
            st.markdown("### <i class='bx bxs-download'></i> Download Hasil", unsafe_allow_html=True)
            
            # Tambahkan info bobot ke hasil
            result_with_weights = result_df.copy()
            
            csv = result_with_weights.to_csv(index=False)
            st.download_button(
                type="primary",
                label="Download Hasil Ranking (CSV)",
                data=csv,
                file_name="hasil_rekomendasi_kost.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        except ValueError as e:
            st.error(f"❌ {str(e)}")
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan dalam perhitungan: {str(e)}")

else:
    # Tampilan awal jika belum upload file
    st.info("👆 Silakan upload file dataset kost untuk memulai analisis MOORA")
    
    st.markdown("### 📝 Format Dataset yang Diperlukan")
    st.write("Dataset harus memiliki kolom-kolom berikut:")
    
    example_data = {
        'Name': ['Kost_A', 'Kost_B', 'Kost_C'],
        'Price': [1800, 900, 2000],
        'Distance': [2.5, 1.0, 3.5],
        'Size': [15, 12, 18],
        'Wifi': [50, 100, 75],
        'Security_Score': [8, 9, 7]
    }
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)

    if os.path.exists("data/dataset_template.csv"):
        with open("data/dataset_template.csv", "rb") as f:
            csv = f.read().decode("utf-8")
        st.download_button(
            type="primary",
            label="Download Template Dataset (CSV)",
            data=csv,
            file_name="dataset_template.csv",
            mime="text/csv",
            use_container_width=True
        )


# Footer
st.markdown("---")
st.markdown("""
<div class='footer d-flex justify-content-center align-items-center gap-2 fs-6'>
    <a href='' target='_self'>SIREKMA</a>
    |
    <a href='https://github.com/Superior231/sirekma' class='text-center d-flex align-items-center gap-1'><i class='bx bxl-github fs-6'></i> GitHub</a>
    |
    <span>Copyright &copy;2025 </span><a href='https://hikmal-falah.com/' class='text-primary'>Hikmal Falah.</a>
</div>
""", unsafe_allow_html=True)