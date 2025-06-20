from flask import Flask, render_template, request, send_from_directory 
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import numpy as np
import os

app = Flask(__name__) #inisialisasi flask
app.config['UPLOAD_FOLDER'] = 'uploads/' #variabel yg sudah saya definisikan yaitu folder uploads

def get_image_info(image_path):
    with Image.open(image_path) as img: #membuka gambar
        width, height = img.size #mengambil ukuran gambar panjang lebar
        mode = img.mode #mengambil mode gambar, misal L untuk grayscale
        pixels = img.load() #mengeload data piksel gambar
        middle_pixel = None #inisialisasi variabel kosong
        if width > 0 and height > 0: #mengecek apakah lebar dan panjangnya 0?
            middle_pixel = pixels[width // 2, height // 2] #membagi nilai height dan width dengan 2, agar focus ketengah
            #return ke 4 variabel seperti biasa
        return {
            'width': width,
            'height': height,
            'mode': mode,
            'middle_pixel': middle_pixel
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None #inisialisasi variabel kosong
    image_info = None #inisialisasi variabel kosong
    if request.method == 'POST': #Kondisi ini memeriksa apakah metode request adalah POST
        if 'image' not in request.files: #memeriksa apakah ada file gambar?
            return 'Tidak ada gambar'#jika tidak ada gambar maka akan muncul pesan ini
        file = request.files['image'] #mengambil file gambar
        if file.filename == '': #Kondisi ini memeriksa apakah file gambar telah dipilih.
            return 'Gambar tidak terpilih' #jika tidak ada gambar yg dipilih maka akan muncul pesan ini
        if file: #Kondisi ini memvalidasi apakah file gambar ada.
            filename = file.filename #Variabel filename diinisialisasi dengan nama file gambar.
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) #Variabel filepath diinisialisasi dengan path file gambar yang akan disimpan.
            if not os.path.exists(app.config['UPLOAD_FOLDER']): #memeriksa apakah folder uploads ada
                os.makedirs(app.config['UPLOAD_FOLDER']) #jika tidak ada maka akan membuat folder uploads
            file.save(filepath) #file gambar disimpan di folder ulpoads
            image_url = filename  #Variabel image_url diinisialisasi dengan nama file gambar.
            image_info = get_image_info(filepath) #informasi dari fungsi get_image_info
    return render_template('index.html', image_url=image_url, image_info=image_info) #dikembalikan ke index.html

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename) #mengirim file yg di upload ke browser

@app.route('/grayscale', methods=['POST'])
def grayscale():
    filename = request.form.get('filename') #mengambil filegambar dari form html
    if not filename: #memeriksa apakah filegambar ada
        return 'Tidak ada gambar', 400 #jika tidak ada gambar maka akan muncul pesan ini
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #membuat jalur (path) ke filegambar asli di server
    with Image.open(img_path) as img: #dibuka gambarnya
        gray_img = img.convert('L') #di convert ke grayscale
        gray_filename = 'grayscale_' + filename #membuat nama file baru 
        gray_path = os.path.join(app.config['UPLOAD_FOLDER'], gray_filename) #menyimpan filegambar di folder uploads
        gray_img.save(gray_path) #menyimpan filegambar
    return render_template('index.html', image_url=gray_filename, image_info=get_image_info(gray_path)) #dikembalikan ke index.html

@app.route('/binary', methods=['POST'])
def binary():
    filename = request.form.get('filename') #mengambil filegambar dari form html
    if not filename: #mengcek apakah filegambar ada
        return 'Tidak ada gambar', 400 #jika ga ada muncul pesan ini
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #membuat jalur (path) ke filegambar asli di server
    with Image.open(img_path) as img: #dibuka gambarnya
        gray_img = img.convert('L') #di convert ke grayscale
        binary_img = gray_img.point(lambda x: 0 if x < 128 else 255, '1')  #memetakan gambar dengan treshold 128
        binary_filename = 'binary_' + filename #menambahkan nama file baru
        binary_path = os.path.join(app.config['UPLOAD_FOLDER'], binary_filename) #membuat jalur untuk menyimpan filegambar
        binary_img.save(binary_path) #menyimpan filegambar sesuai path (jalur) nya
    return render_template('index.html', image_url=binary_filename, image_info=get_image_info(binary_path)) #dikirim ke index.html

@app.route('/negative', methods=['POST'])
def negative():
    filename = request.form.get('filename') #mengambil filegambar dari form html
    if not filename: #mengecek file gambar
        return 'Tidak ada gambar', 400 #kirim peszan ini jika tidak ada
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #membuat jalur (path) ke filegambar asli di server
    # Buka gambar
    with Image.open(img_path) as img:
        # Convert ke negatif
        negative_img = Image.eval(img, lambda x: 255 - x)  # Mengubah setiap piksel
        negative_filename = 'negative_' + filename #menambahkan nama file baru
        negative_path = os.path.join(app.config['UPLOAD_FOLDER'], negative_filename) #membuat jalur sebelum disimpan
        negative_img.save(negative_path) #menyimpan filegambar
    return render_template('index.html', image_url=negative_filename, image_info=get_image_info(negative_path)) #kirim ke index.html

@app.route('/brighten', methods=['POST'])
def brighten():
    filename = request.form.get('filename') #mengambil filegambar dari form html
    if not filename: #mengecek file gambar
        return 'Tidak ada gambar', 400 #sama seperti diatas
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #membuat jalur (path) ke filegambar asli di server
    
    with Image.open(img_path) as img: #dibuka gambarnya
        enhancer = ImageEnhance.Brightness(img) #membuat objek enhancer
        bright_img = enhancer.enhance(1.5)  #membuat gambar lebih terang
        bright_filename = 'brighten_' + filename #sama sebagai diatas
        bright_path = os.path.join(app.config['UPLOAD_FOLDER'], bright_filename) #membuat jalur sebelum disimpan
        bright_img.save(bright_path) #menyimpan filegambar
    return render_template('index.html', image_url=bright_filename, image_info=get_image_info(bright_path)) #sama seperti diatas

@app.route('/translate', methods=['POST'])
def translate():
    filename = request.form.get('filename') #mengambil filegambar dari form html
    tx = int(request.form.get('tx', 0)) #mengambil koordinat x
    ty = int(request.form.get('ty', 0)) #mengambil koordinat y
    if not filename: #mengecek file gambar
        return 'Tidak ada gambar', 400 #sama seperti diatas
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #membuat jalur (path) ke filegambar asli di server

    with Image.open(img_path) as img: #dibuka gambarnya
        new_img = Image.new('RGB', img.size ,color=(255, 255, 255)) #membuat gambar baru / canvas
        new_img.paste(img, (tx, ty)) #menggabungkan gambar
        translated_filename = f'translated_{filename}' #menambahkan nama file
        translated_path = os.path.join(app.config['UPLOAD_FOLDER'], translated_filename) #membuat jalur sebelum disimpan
        new_img.save(translated_path) #menyimpan filegambar
    return render_template('index.html', image_url=translated_filename, image_info=get_image_info(translated_path)) #sama seperti diatas

@app.route('/rotate', methods=['POST'])
def rotate():
    filename = request.form.get('filename') #mengambil filegambar dari form html
    angle = float(request.form.get('angle', 0)) #mengambil sudut rotasi
    if not filename: #mengecek file gambar
        return 'Tidak ada gambar', 400 #sama seperti diatas
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #membuat jalur (path) ke filegambar asli di server

    with Image.open(img_path) as img: #dibuka gambarnya
        rotated_img = img.rotate(-angle, expand=True)  #rotasi gambar
        rotated_filename = f'rotated_{filename}' #menambahkan nama file
        rotated_path = os.path.join(app.config['UPLOAD_FOLDER'], rotated_filename) #membuat jalur sebelum disimpan
        rotated_img.save(rotated_path) #menyimpan filegambar
    return render_template('index.html', image_url=rotated_filename, image_info=get_image_info(rotated_path)) #sama seperti diatas

@app.route('/flip', methods=['POST'])
def flip():
    filename = request.form.get('filename') #mengambil filegambar dari form html
    mode = request.form.get('mode', 'horizontal') #mengambil mode flip
    if not filename: #mengecek file gambar
        return 'Tidak ada gambar', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #membuat jalur (path) ke filegambar asli di server

    with Image.open(img_path) as img:
        if mode == 'horizontal': #mengecek mode
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT) #membalik gambar ke kiri kanan
        elif mode == 'vertical': #mengecek mode
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM) #membalik gambar ke atas bawah
        else:
            return 'Flip gagal dimuat', 400
        flipped_filename = f'flipped_{mode}_{filename}' #menambahkan nama file
        flipped_path = os.path.join(app.config['UPLOAD_FOLDER'], flipped_filename) #membuat jalur sebelum disimpan
        flipped_img.save(flipped_path)
    return render_template('index.html', image_url=flipped_filename, image_info=get_image_info(flipped_path)) #sama seperti diatas

Image.MAX_IMAGE_PIXELS = None
@app.route('/scale', methods=['POST'])
def scale():
    filename = request.form.get('filename') #ambil filegambar
    scale_factor = float(request.form.get('scale', 1.0)) #ambil faktor skala

    if scale_factor > 5:  #maksimal scale
        return 'Gambar terlalu besar', 400

    if not filename: #mengecek file gambar
        return 'Tidak ada gambar', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #membuat jalur (path) ke filegambar asli di server

    with Image.open(img_path) as img: #buka gambar
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor)) #mengubah ukuran
        scaled_img = img.resize(new_size, Image.LANCZOS) #mengubah ukuran dengan interpolasi lanczos
        scaled_filename = f'scaled_{filename}' #menambahkan nama file
        scaled_path = os.path.join(app.config['UPLOAD_FOLDER'], scaled_filename) #membuat jalur sebelum disimpan
        scaled_img.save(scaled_path)
    return render_template('index.html', image_url=scaled_filename, image_info=get_image_info(scaled_path))

@app.route('/histogram', methods=['POST'])
def histogram():
    filename = request.form.get('filename')
    if not filename:
        return 'Tidak ada gambar', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with Image.open(img_path) as img:
        gray_img = img.convert('L') #conveert ke grayscale
        pixels = list(gray_img.getdata()) #mengambil data piksel dan menjadikannya 1 baris (list)
        # Buat histogram plot
        plt.figure(figsize=(6,4), facecolor="#1c26b9") #membuat ukuran plot histogram
        plt.hist(pixels, bins=256, range=(0,255), color='#ff6f61') #membuat histogram
        plt.title('Histogram Gambar') #menambahkan judul
        plt.xlabel('Intensitas Piksel') #menambahkan label
        plt.ylabel('Frekuensi') #menambahkan label
        hist_filename = f'hist_{filename}.png'
        hist_path = os.path.join(app.config['UPLOAD_FOLDER'], hist_filename)
        plt.savefig(hist_path)
        plt.close() #menutup plot
    return render_template('index.html', image_url=filename, histogram_url=hist_filename)


@app.route('/frequency', methods=['POST'])
def frequency():
    filename = request.form.get('filename')
    if not filename:
        return 'Tidak ada gambar', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with Image.open(img_path) as img:
        gray_img = img.convert('L') #convert ke grayscale
        img_array = np.array(gray_img) #mengubah gambar ke array
        # Hitung FFT 2D
        f = np.fft.fft2(img_array) #melakukan FFT 2D
        fshift = np.fft.fftshift(f) #melakukan FFT shift
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)  #menghitung spektrum frekuensi

        # Normalisasi ke 0-255
        magnitude_spectrum = np.asarray(magnitude_spectrum, dtype=np.float32) #mengubah tipe data ke float32
        magnitude_spectrum -= magnitude_spectrum.min() #mengurangi nilai minimum
        magnitude_spectrum /= magnitude_spectrum.max() #mengurangi nilai maksimum
        magnitude_spectrum *= 255 #mengalikan dengan 255
        magnitude_spectrum = magnitude_spectrum.astype(np.uint8) #mengubah tipe data ke uint8

        # Simpan gambar spektrum frekuensi
        freq_img = Image.fromarray(magnitude_spectrum) #mengubah array ke gambar
        freq_filename = f'frequency_{filename}' #menambahkan nama file
        freq_path = os.path.join(app.config['UPLOAD_FOLDER'], freq_filename) #membuat jalur sebelum disimpan
        freq_img.save(freq_path) #menyimpan filegambar

    return render_template('index.html', image_url=filename, frequency_url=freq_filename)



if __name__ == '__main__': #menjalankan program
    app.run(debug=True) #menjalankan program
