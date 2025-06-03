from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import numpy as np
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

def get_image_info(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        mode = img.mode
        pixels = img.load()
        middle_pixel = None
        if width > 0 and height > 0:
            middle_pixel = pixels[width // 2, height // 2]
        return {
            'width': width,
            'height': height,
            'mode': mode,
            'middle_pixel': middle_pixel
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None
    image_info = None
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No file part'
        file = request.files['image']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Pastikan folder upload ada
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(filepath)
            image_url = filename  # hanya filename karena nanti dipanggil via route khusus
            image_info = get_image_info(filepath)
    return render_template('index.html', image_url=image_url, image_info=image_info)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/grayscale', methods=['POST'])
def grayscale():
    filename = request.form.get('filename')
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Buka gambar
    with Image.open(img_path) as img:
        gray_img = img.convert('L')  # convert ke grayscale
        # simpan hasil dengan nama baru
        gray_filename = 'grayscale_' + filename
        gray_path = os.path.join(app.config['UPLOAD_FOLDER'], gray_filename)
        gray_img.save(gray_path)
    return render_template('index.html', image_url=gray_filename, image_info=get_image_info(gray_path))

@app.route('/binary', methods=['POST'])
def binary():
    filename = request.form.get('filename')
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Buka gambar
    with Image.open(img_path) as img:
        # Convert ke grayscale terlebih dahulu
        gray_img = img.convert('L')
        # Kemudian convert ke biner
        binary_img = gray_img.point(lambda x: 0 if x < 128 else 255, '1')  # threshold 128
        # Simpan hasil dengan nama baru
        binary_filename = 'binary_' + filename
        binary_path = os.path.join(app.config['UPLOAD_FOLDER'], binary_filename)
        binary_img.save(binary_path)
    return render_template('index.html', image_url=binary_filename, image_info=get_image_info(binary_path))

@app.route('/negative', methods=['POST'])
def negative():
    filename = request.form.get('filename')
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Buka gambar
    with Image.open(img_path) as img:
        # Convert ke negatif
        negative_img = Image.eval(img, lambda x: 255 - x)  # Mengubah setiap piksel
        # Simpan hasil dengan nama baru
        negative_filename = 'negative_' + filename
        negative_path = os.path.join(app.config['UPLOAD_FOLDER'], negative_filename)
        negative_img.save(negative_path)
    return render_template('index.html', image_url=negative_filename, image_info=get_image_info(negative_path))

@app.route('/brighten', methods=['POST'])
def brighten():
    filename = request.form.get('filename')
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    with Image.open(img_path) as img:
        enhancer = ImageEnhance.Brightness(img)
        bright_img = enhancer.enhance(1.5)  # faktor pencerahan 1.5, bisa disesuaikan
        bright_filename = 'brighten_' + filename
        bright_path = os.path.join(app.config['UPLOAD_FOLDER'], bright_filename)
        bright_img.save(bright_path)
    return render_template('index.html', image_url=bright_filename, image_info=get_image_info(bright_path))

@app.route('/translate', methods=['POST'])
def translate():
    filename = request.form.get('filename')
    tx = int(request.form.get('tx', 0))
    ty = int(request.form.get('ty', 0))
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with Image.open(img_path) as img:
        # Buat canvas baru dengan ukuran sama dan mode sama dengan latar belakang hitam
        new_img = Image.new(img.mode, img.size)
        # Paste gambar asal ke posisi yang digeser (translasi)
        new_img.paste(img, (tx, ty))
        translated_filename = f'translated_{filename}'
        translated_path = os.path.join(app.config['UPLOAD_FOLDER'], translated_filename)
        new_img.save(translated_path)
    return render_template('index.html', image_url=translated_filename, image_info=get_image_info(translated_path))

@app.route('/rotate', methods=['POST'])
def rotate():
    filename = request.form.get('filename')
    angle = float(request.form.get('angle', 0))
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with Image.open(img_path) as img:
        rotated_img = img.rotate(-angle, expand=True)  # rotate counterclockwise, expand canvas
        rotated_filename = f'rotated_{filename}'
        rotated_path = os.path.join(app.config['UPLOAD_FOLDER'], rotated_filename)
        rotated_img.save(rotated_path)
    return render_template('index.html', image_url=rotated_filename, image_info=get_image_info(rotated_path))

@app.route('/flip', methods=['POST'])
def flip():
    filename = request.form.get('filename')
    mode = request.form.get('mode', 'horizontal')
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with Image.open(img_path) as img:
        if mode == 'horizontal':
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif mode == 'vertical':
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            return 'Invalid flip mode', 400
        flipped_filename = f'flipped_{mode}_{filename}'
        flipped_path = os.path.join(app.config['UPLOAD_FOLDER'], flipped_filename)
        flipped_img.save(flipped_path)
    return render_template('index.html', image_url=flipped_filename, image_info=get_image_info(flipped_path))

Image.MAX_IMAGE_PIXELS = None
@app.route('/scale', methods=['POST'])
def scale():
    filename = request.form.get('filename')
    scale_factor = float(request.form.get('scale', 1.0))

    if scale_factor > 5:  
        return 'Scale factor too large', 400

    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with Image.open(img_path) as img:
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
        scaled_img = img.resize(new_size, Image.LANCZOS)
        scaled_filename = f'scaled_{filename}'
        scaled_path = os.path.join(app.config['UPLOAD_FOLDER'], scaled_filename)
        scaled_img.save(scaled_path)
    return render_template('index.html', image_url=scaled_filename, image_info=get_image_info(scaled_path))

@app.route('/histogram', methods=['POST'])
def histogram():
    filename = request.form.get('filename')
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with Image.open(img_path) as img:
        # Convert ke grayscale untuk histogram intensitas
        gray_img = img.convert('L')
        pixels = list(gray_img.getdata())
        # Buat histogram plot
        plt.figure(figsize=(6,4))
        plt.hist(pixels, bins=256, range=(0,255), color='black')
        plt.title('Histogram Intensity')
        plt.xlabel('Pixel Intensity')
        plt.ylabel('Frequency')
        hist_filename = f'hist_{filename}.png'
        hist_path = os.path.join(app.config['UPLOAD_FOLDER'], hist_filename)
        plt.savefig(hist_path)
        plt.close()
    return render_template('index.html', image_url=filename, histogram_url=hist_filename)


@app.route('/frequency', methods=['POST'])
def frequency():
    filename = request.form.get('filename')
    if not filename:
        return 'No filename provided', 400
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with Image.open(img_path) as img:
        gray_img = img.convert('L')
        img_array = np.array(gray_img)
        # Hitung FFT 2D
        f = np.fft.fft2(img_array)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)  # +1 to avoid log(0)

        # Normalisasi ke 0-255
        magnitude_spectrum = np.asarray(magnitude_spectrum, dtype=np.float32)
        magnitude_spectrum -= magnitude_spectrum.min()
        magnitude_spectrum /= magnitude_spectrum.max()
        magnitude_spectrum *= 255
        magnitude_spectrum = magnitude_spectrum.astype(np.uint8)

        # Simpan gambar spektrum frekuensi
        freq_img = Image.fromarray(magnitude_spectrum)
        freq_filename = f'frequency_{filename}'
        freq_path = os.path.join(app.config['UPLOAD_FOLDER'], freq_filename)
        freq_img.save(freq_path)

    return render_template('index.html', image_url=filename, frequency_url=freq_filename)



if __name__ == '__main__':
    app.run(debug=True)
