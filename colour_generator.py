from PIL import Image
import numpy as np
import scipy.cluster
from flask import Flask, render_template, request, flash
import os
from colorthief import ColorThief


app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = 'static/uploads/'


# -------------------- FUNCTIONS -----------------------------#

# -------------------- COLOR GENERATION ----------------------#
def color_generator(file):
    img = Image.open(file)
    imagen = img.load()
    width_img = img.size[0]
    length_img = img.size[1]
    num_colors = width_img * length_img
    colors = np.ndarray((num_colors, 3), dtype=float)
    h = 0
    for i in range(width_img):
        for j in range(length_img):
            colors[h] = [imagen[i, j][0], imagen[i, j][1], imagen[i, j][2]]
            h += 1

    # Finding clusters (10 clusters):
    codes, dist = scipy.cluster.vq.kmeans(colors, 10)
    # Finding count of occurrences in clusters
    vecs, dist = scipy.cluster.vq.vq(colors, codes)  # assign codes
    counts, bins = np.histogram(vecs, len(codes))
    colors_total = counts.sum()
    # List of RGB colors and percentage of cluster within the image
    color_list = [[round(codes[i][0]), round(codes[i][1]), round(codes[i][2]), round(counts[i]*100/colors_total, 2)] for i in range(len(counts))]
    # List to numpy array to rearrange values with percentages in descending order
    color_array = np.array(color_list)
    order = np.argsort(1 / color_array[:, 3])
    # Numpy array back to list to pass to html template
    final_color_array = color_array[order, :].tolist()
    return final_color_array


def color_palette(file):
    color_thief = ColorThief(file)
    # get a maximum of 10 dominant colors from image file
    palette = color_thief.get_palette(color_count=10, quality=1)
    print(palette)
    return palette



# ---------------------- WEBSITE DEVELOPMENT -------------------------------#
# Home Page
@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        if request.files:
            file = request.files['file']
            file_extension = file.filename.split('.')[1].lower()
            if file_extension != 'png' and file_extension != 'jpg' and file_extension != 'jpeg' and file_extension != 'gif':
                flash('Please select a file with extension .png, .jpg, jpeg, or .gif')
                return render_template('index.html', filename='')
            elif file.filename == '':
                flash('No image selected for uploading')
                return render_template('index.html', filename='')
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                filename = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                flash('Image successfully uploaded and displayed below')
                color_list = color_generator(filename)
                color_list2 = color_palette(filename)
                return render_template('index.html', filename=f'static/uploads/{file.filename}', colors=color_list,
                                       colors2=color_list2)

        else:
            flash('Please select an image')
            return render_template('index.html', filename='')

    else:
        return render_template("index.html", filename='')


if __name__ == "__main__":
    app.run(debug=True)