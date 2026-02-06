import os
import sqlite3
import qrcode
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- GENEL AYARLAR ---
DB_NAME = 'stok_takip.db'  # Artık tek ve sabit bir isim
FIRMA_ADI = "Stok Takip Sistemi" # Burayı istediğin gibi değiştirebilirsin

app.config['UPLOAD_FOLDER'] = 'static/resimler'
app.config['QR_FOLDER'] = 'static/qr'

# --- SİGORTA: Klasörler yoksa otomatik oluştur ---
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['QR_FOLDER']):
    os.makedirs(app.config['QR_FOLDER'])

# --- VERİTABANI BAĞLANTISI (Yardımcı Fonksiyon) ---
def baglanti_al():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Verilere isimle erişmek için (dict gibi)
    return conn

# --- VERİTABANI KURULUMU ---
def veritabani_kur():
    conn = baglanti_al()
    imlec = conn.cursor()
    # Tablo yoksa oluşturur, varsa dokunmaz.
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS stoklar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_adi TEXT,
            ton TEXT,
            en INTEGER,
            boy INTEGER,
            adet INTEGER,
            resim TEXT,
            qr_resmi TEXT
        )
    """)
    conn.commit()
    conn.close()

# Uygulama başlarken veritabanını kontrol et
veritabani_kur()

# --- SAYFALAR ---

@app.route('/')
def anasayfa():
    # Firma adını HTML'e gönderiyoruz
    return render_template('index.html', baslik=FIRMA_ADI)

@app.route('/panel')
def panel():
    conn = baglanti_al()
    imlec = conn.cursor()
    
    imlec.execute("SELECT count(*) FROM stoklar")
    toplam_palet = imlec.fetchone()[0]
    
    imlec.execute("SELECT en, boy, adet FROM stoklar")
    tum_stoklar = imlec.fetchall()
    
    toplam_m2 = 0
    for stok in tum_stoklar:
        # stok[0]=en, stok[1]=boy, stok[2]=adet
        m2 = (stok['en'] * stok['boy'] * stok['adet']) / 10000
        toplam_m2 += m2
        
    imlec.execute("SELECT count(*) FROM stoklar WHERE adet < 20")
    kritik = imlec.fetchone()[0]

    conn.close()
    return render_template('panel.html', palet_sayisi=toplam_palet, toplam_m2=round(toplam_m2, 2), kritik=kritik, baslik=FIRMA_ADI)

@app.route('/mal-kabul', methods=['GET', 'POST'])
def mal_kabul():
    if request.method == 'POST':
        gelen_ad = request.form['urun_adi']
        gelen_ton = request.form['ton']
        gelen_en = int(request.form['en'])
        gelen_boy = int(request.form['boy'])
        gelen_adet = int(request.form['adet'])
        
        dosya_adi = ""
        if 'resim' in request.files:
            dosya = request.files['resim']
            if dosya.filename != '':
                dosya_adi = secure_filename(dosya.filename)
                dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosya_adi))

        conn = baglanti_al()
        imlec = conn.cursor()
        
        imlec.execute("""
            SELECT id, adet FROM stoklar 
            WHERE urun_adi=? AND ton=? AND en=? AND boy=?
        """, (gelen_ad, gelen_ton, gelen_en, gelen_boy))
        
        var_olan = imlec.fetchone()
        
        if var_olan:
            kayit_id = var_olan['id']
            yeni_adet = var_olan['adet'] + gelen_adet
            imlec.execute("UPDATE stoklar SET adet=? WHERE id=?", (yeni_adet, kayit_id))
        else:
            imlec.execute("""
                INSERT INTO stoklar (urun_adi, ton, en, boy, adet, resim, qr_resmi) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (gelen_ad, gelen_ton, gelen_en, gelen_boy, gelen_adet, dosya_adi, 'temp'))
            
            yeni_id = imlec.lastrowid
            
            # QR Linki (Şimdilik Localhost)
            qr_icerigi = f"http://127.0.0.1:5000/kesim/{yeni_id}"
            qr_img = qrcode.make(qr_icerigi)
            qr_dosya_adi = f"qr_{yeni_id}.png"
            qr_img.save(os.path.join(app.config['QR_FOLDER'], qr_dosya_adi))
            
            imlec.execute("UPDATE stoklar SET qr_resmi=? WHERE id=?", (qr_dosya_adi, yeni_id))
        
        conn.commit()
        conn.close()
        return redirect(url_for('stoklar'))

    return render_template('mal_kabul.html', baslik=FIRMA_ADI)

@app.route('/stoklar')
def stoklar():
    conn = baglanti_al()
    imlec = conn.cursor()
    imlec.execute("SELECT * FROM stoklar ORDER BY urun_adi ASC")
    veriler = imlec.fetchall()
    conn.close()
    
    islenmis_liste = []
    toplam_m2 = 0 
    
    for mermer in veriler:
        # Row factory kullandığımız için dict gibi davranır, ama listeye çevirip ekleyelim
        # Veya template içinde mermer['en'] diye kullanabiliriz.
        # Kolaylık olsun diye eski mantık (list conversion) devam edebilir veya dictionary kullanabilirsin.
        # Burada dictionary yapısını koruyup m2'yi hesaplayıp template'e nesne olarak göndermek daha modern olurdu
        # Ama senin mevcut HTML yapını bozmamak için listeye çeviriyorum:
        
        m_liste = list(mermer) # [id, ad, ton, en, boy, adet, resim, qr]
        m2 = (mermer['en'] * mermer['boy'] * mermer['adet']) / 10000
        m_liste.append(round(m2, 2))
        
        islenmis_liste.append(m_liste)
        toplam_m2 += m2

    return render_template('stoklar.html', stok_listesi=islenmis_liste, genel_toplam=round(toplam_m2, 2), baslik=FIRMA_ADI)

@app.route('/sil/<int:id>')
def stok_sil(id):
    conn = baglanti_al()
    imlec = conn.cursor()
    imlec.execute("DELETE FROM stoklar WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('stoklar'))

@app.route('/kesim/<int:id>', methods=['GET', 'POST'])
def kesim_yap(id):
    conn = baglanti_al()
    imlec = conn.cursor()
    imlec.execute("SELECT * FROM stoklar WHERE id = ?", (id,))
    secilen_mermer = imlec.fetchone()

    if request.method == 'POST':
        try:
            kesilen_adet = int(request.form['kesilen_adet'])
        except ValueError:
            conn.close()
            return render_template('kesim.html', mermer=secilen_mermer, hata_mesaji="Lütfen sayı girin.", baslik=FIRMA_ADI)

        eski_adet = secilen_mermer['adet']
        yeni_adet = eski_adet - kesilen_adet
        
        if yeni_adet < 0:
            conn.close()
            return render_template('kesim.html', mermer=secilen_mermer, hata_mesaji="Stok yetersiz!", baslik=FIRMA_ADI)

        if yeni_adet == 0:
             imlec.execute("DELETE FROM stoklar WHERE id = ?", (id,))
        else:
            imlec.execute("UPDATE stoklar SET adet = ? WHERE id = ?", (yeni_adet, id))
            
        conn.commit()
        conn.close()
        return redirect(url_for('stoklar'))

    conn.close()
    return render_template('kesim.html', mermer=secilen_mermer, baslik=FIRMA_ADI)

if __name__ == '__main__':
    app.run(debug=True)