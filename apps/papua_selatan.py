import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os


def app():
    # Dataset untuk select user
    df = pd.read_csv("dataset/trx_93_product_lokasi_user.csv")

    # Ambil daftar kabupaten unik
    kabupaten_list = df["nama kabupaten"].unique()

    # Tampilkan select box untuk memilih kabupaten
    selected_kabupaten = st.selectbox("Pilih Kabupaten:", kabupaten_list)

    # Filter data berdasarkan kabupaten yang dipilih
    filtered_data_kabupaten = df[df["nama kabupaten"] == selected_kabupaten]

    # Ambil daftar kecamatan unik untuk kabupaten yang dipilih
    kecamatan_list = filtered_data_kabupaten["nama kecamatan"].unique()

    # Tampilkan select box untuk memilih kecamatan
    selected_kecamatan = st.selectbox("Pilih Kecamatan:", kecamatan_list)

    # Filter data berdasarkan kecamatan yang dipilih
    filtered_data_kecamatan = filtered_data_kabupaten[
        filtered_data_kabupaten["nama kecamatan"] == selected_kecamatan
    ]

    # Ambil daftar nama pengguna unik
    user_list = filtered_data_kecamatan["full_name"].unique()

    # Tampilkan select box untuk memilih nama pengguna
    selected_user = st.selectbox("Pilih Nama Pengguna:", user_list)

    # Data Model Rekomendasi
    df_model = (
        df.groupby(["full_name", "product_name"])["product_name"]
        .count()
        .reset_index(name="count")
    )

    # Model rekomendasi
    def rekomendasi_produk(df_model, selected_user, user_similarity_threshold=0.3, n=1):
        # Membuat pivot table
        matrix = df_model.pivot_table(
            index="full_name", columns="product_name", values="count"
        )

        # Mengisi nilai NaN dengan 0
        matrix_filled = matrix.fillna(0)

        # Menghitung kemiripan kosinus antar pengguna
        user_similarity_cosine = cosine_similarity(matrix_filled)

        # Konversi matriks kemiripan menjadi DataFrame
        user_similarity_df = pd.DataFrame(
            user_similarity_cosine,
            index=matrix_filled.index,
            columns=matrix_filled.index,
        )

        # Dapatkan pengguna mirip yang melebihi ambang batas kemiripan
        similar_users = user_similarity_df[
            user_similarity_df[selected_user] > user_similarity_threshold
        ][selected_user]

        # Keluarkan pengguna yang dipilih dari daftar
        similar_users = similar_users.drop(index=selected_user)

        # Urutkan pengguna mirip berdasarkan nilai kemiripan secara menurun dan ambil top n
        top_similar_users = similar_users.sort_values(ascending=False).head(n)

        # Produk yang dibeli oleh user
        bought_products = set(
            df[df["full_name"] == selected_user]["product_name"].values
        )

        # Produk yang dibeli oleh pengguna mirip
        similar_users_bought_products = set(
            df[df["full_name"].isin(top_similar_users.index)]["product_name"].values
        )

        # Produk yang direkomendasikan adalah produk yang dibeli oleh user mirip tapi belum dibeli oleh user yang dipilih
        recommended_products = list(similar_users_bought_products - bought_products)

        # Batasi rekomendasi produk ke top 3 (atau lebih jika diinginkan)
        recommended_products = recommended_products[:3]

        if not recommended_products:
            recommended_products = ["Tidak Ada Rekomendasi Produk"]

        return recommended_products

    # Direktori tempat gambar-gambar produk disimpan
    image_dir = "gambar"

    # Fungsi untuk mendapatkan path gambar berdasarkan nama produk
    def get_product_image_path(product_name):
        # Ubah nama produk menjadi lowercase dan ganti spasi dengan underscore
        image_name = product_name.lower().replace(" ", "_") + ".png"
        # Gabungkan dengan direktori gambar untuk mendapatkan path lengkap
        image_path = os.path.join(image_dir, image_name)
        return image_path

    if st.button("Rekomendasikan Produk"):
        # Rekomendasi produk
        recommended_products = rekomendasi_produk(df_model, selected_user)

        # Tampilkan rekomendasi produk
        for product_name in recommended_products:
            col1, col2 = st.columns([1, 3])
            with col1:
                image_path = get_product_image_path(product_name)
                st.image(image_path, caption=product_name, use_column_width=True)
