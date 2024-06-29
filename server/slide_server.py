from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os
from io import BytesIO

OPENSLIDE_PATH = os.path.join(os.getcwd(), 'openslide', 'bin')
if hasattr(os, 'add_dll_directory'):
    with os.add_dll_directory(OPENSLIDE_PATH):
        import openslide
        import openslide.deepzoom
        from openslide import open_slide
        from PIL import Image
        import numpy as np
        from matplotlib import pyplot as plt
        from openslide.deepzoom import DeepZoomGenerator

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

TILE_SIZE = 256
OVERLAP = 0

folder_upload_path = r"D:\Work\Mesoco\slide-viewer\upload"

@app.route('/slide/<string:slidename>/<int:level>/<int:col>_<int:row>.jpeg')
def get_tile(slidename, level, col, row):
    try:
        slide_path = os.path.join(folder_upload_path, slidename)
        slide = openslide.OpenSlide(slide_path)
        dz_generator = DeepZoomGenerator(slide, tile_size=TILE_SIZE, overlap=OVERLAP)
        tile = dz_generator.get_tile(level, (col, row))
        buf = BytesIO()
        tile.save(buf, format='JPEG')
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg')
    except Exception as e:
        app.logger.error(f"Error generating tile: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/slide/metadata/<string:slidename>')
def get_metadata(slidename):
    slide_path = os.path.join(folder_upload_path, slidename)
    slide = openslide.OpenSlide(slide_path)
    metadata = {
        "scanner": slide.properties.get(openslide.PROPERTY_NAME_VENDOR),
        "mpp_x": float(slide.properties.get(openslide.PROPERTY_NAME_MPP_X, 0)),
        "mpp_y": float(slide.properties.get(openslide.PROPERTY_NAME_MPP_Y, 0)),
        "dimensions": slide.dimensions,
        "level_count": slide.level_count,
        "level_dimensions": slide.level_dimensions,
        "level_downsamples": slide.level_downsamples,
        "tile_size": TILE_SIZE,
        "overlap": OVERLAP,
        "slidename": os.path.basename(slide_path).split('.')[0]
    }
    return jsonify(metadata)

if __name__ == '__main__':
    app.run(debug=True)