from flask import Flask, render_template, request, send_file
from google_play_scraper import reviews, Sort
import pandas as pd
import re 
import os 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data_hasil = []
    pesan_error = ""
    jumlah_target = 100 # Default awal

    if request.method == 'POST':
        url_target = request.form.get('url_input')
        
        # Ambil input jumlah (Kalau kosong/error, default ke 100)
        try:
            jumlah_target = int(request.form.get('jumlah_input', 100))
        except:
            jumlah_target = 100

        print(f"Memproses URL: {url_target} | Target: {jumlah_target} ulasan")
        
        try:
            # Cari ID aplikasi pake Regex (Pola: id=com.nama.aplikasi)
            match = re.search(r'id=([a-zA-Z0-9._]+)', url_target)
            
            if match:
                app_id = match.group(1)
                
                # Scrape Data Sesuai Jumlah Input User
                hasil_reviews, _ = reviews(
                    app_id,
                    lang='id', 
                    country='id', 
                    sort=Sort.NEWEST, 
                    count=jumlah_target 
                )
                
                # Masukin ke list data_hasil
                for ulasan in hasil_reviews:
                    data_hasil.append({
                        'Waktu': ulasan['at'].strftime('%Y-%m-%d'),
                        'User': ulasan['userName'],
                        'Rating': ulasan['score'],
                        'Komentar': ulasan['content']
                    })
                
                # Simpan CSV otomatis tiap kali sukses scrape
                if data_hasil:
                    df = pd.DataFrame(data_hasil)
                    df.to_csv('hasil_ulasan.csv', index=False)
                    print(f"Sukses! {len(data_hasil)} data tersimpan.")
                
            else:
                pesan_error = "Link tidak valid! Pastikan link dari Google Play Store."
            
        except Exception as e:
            print(f"ERROR SYSTEM: {e}")
            pesan_error = "Gagal mengambil data. Cek koneksi internet atau link aplikasi."

    # INI BARIS YANG TADI HILANG (PENYEBAB ERROR):
    return render_template('index.html', data=data_hasil, error=pesan_error)

@app.route('/download')
def download_csv():
    # Cek dulu filenya ada gak
    if os.path.exists('hasil_ulasan.csv'):
        return send_file('hasil_ulasan.csv', as_attachment=True)
    return "Belum ada data untuk didownload. Silakan scrape dulu."

if __name__ == '__main__':

    app.run(debug=True)
