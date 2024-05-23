from flask import Flask, request, render_template_string
import automatic1111 as sd
from flask import jsonify


app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Submit Prompt</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        .hidden { display: none; }
    </style>
</head>
<body>
    <h1>Submit a Prompt</h1>
    <form id="promptForm">
        <input type="text" id="promptInput" name="prompt" placeholder="Enter your prompt">
        <button type="submit">Submit</button>
    </form>
    <div id="spinner" class="hidden">Loading...</div>
    <div id="responseArea"></div>

    <script>
        $(document).ready(function() {
            $('#promptForm').submit(function(e) {
                e.preventDefault();
                $('#spinner').removeClass('hidden');
                $.ajax({
                    type: 'POST',
                    url: '/submit',
                    data: { prompt: $('#promptInput').val() },
                    success: function(response) {
                        $('#responseArea').html(response.response);
                        $('#spinner').addClass('hidden');
                    },
                    error: function() {
                        $('#responseArea').html('Error in processing your request.');
                        $('#spinner').addClass('hidden');
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/submit", methods=["POST"])
def submit():
    options = {"sd_model_checkpoint":"AnythingXL_xl.safetensors [8421598e93]"}
    sd.set_options("sdapi/v1/options", **options)
    payload = {
        "prompt": "masterpiece, best quality, colorful and vibrant, landscape, extremely detailed, cozy illustration, illustration, lofi, comforting to look at, a very detailed coffee shop from outside, with a big tree next to it, blue sky, road with pebbles on it, much much detailed, a night scene",  # extra networks also in prompts
        "negative_prompt": "explicit, sensitive, nsfw, low quality, worst quality, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name",
        "seed": 1,
        "steps": 20,
        "width": 512,
        "height": 1024,
        "cfg_scale": 7,
        "sampler_name": "Euler a",
        "n_iter": 1,
        "batch_size": 1,
    }
    base64Image = sd.call_txt2img_api(**payload)
    # import base64
    # from flask import jsonify

    # # Decode the base64 image
    # image_data = base64.b64decode(base64Image)

    # # Convert the image data to a format that can be rendered in the browser
    # image_base64_str = base64.b64encode(image_data).decode('utf-8')
    image_html = f'<img src="data:image/png;base64,{base64Image}" alt="Generated Image"/>'

    # Return the HTML to be rendered in the browser
    return jsonify({"response": image_html})
    # prompt = request.form['prompt']
    # # Simulate a processing delay
    # import time
    # time.sleep(2)
    # return {"response": f"Received prompt: {prompt}"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
