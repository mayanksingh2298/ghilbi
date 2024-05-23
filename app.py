import base64
import zipfile
from flask import Flask, request, render_template_string, send_file
import automatic1111 as sd
options = {"sd_model_checkpoint":"AnythingXL_xl.safetensors [8421598e93]"}
sd.set_options("sdapi/v1/options", **options)
from io import BytesIO

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Submit Prompt</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 flex flex-col items-center justify-center min-h-screen p-4">
    <div class="bg-white rounded-lg shadow-lg w-11/12 sm:w-4/5 mb-4">
        <form id="promptForm" class="space-y-4">
            <textarea id="promptInput" name="prompt" placeholder="Enter your prompt" class="w-full h-24 p-4 border border-gray-300 rounded-md text-lg" style="resize: none;"></textarea>
            <div class="text-gray-500 text-sm mt-2">
                <p>Examples:</p>
                <ul class="list-disc list-inside">
                    <li>A serene landscape with mountains</li>
                    <li>A futuristic city skyline at night</li>
                </ul>
            </div>
            <button type="submit" class="w-full bg-blue-500 text-white py-2 rounded-md text-xl">Submit</button>
        </form>
        <div id="spinner" class="hidden flex justify-center mt-4">
            <div class="spinner border-4 border-t-4 border-blue-500 w-9 h-9 rounded-full animate-spin"></div>
        </div>
    </div>
    <div id="responseArea" class="w-full max-w"></div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#promptForm').submit(function(e) {
                e.preventDefault();
                console.log("Form submission started...");
                $('#spinner').removeClass('hidden');
                $.ajax({
                    type: 'POST',
                    url: '/submit',
                    data: { prompt: $('#promptInput').val() },
                    success: function(response) {
                        console.log("Data received successfully...");
                        console.log(response);
                        var img = $('<img />', { 
                            src: URL.createObjectURL(response),
                            alt: 'Generated Image',
                            class: 'w-full rounded-md mt-4'
                        });
                        $('#responseArea').html(img);
                        $('#spinner').addClass('hidden');
                    },
                    error: function() {
                        $('#responseArea').html('<p class="text-red-500">Error in processing your request.</p>');
                        $('#spinner').addClass('hidden');
                    },
                    complete: function() {
                        console.log("Form submission completed.");
                    },
                    xhrFields: {
                        responseType: 'blob'
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
    
    payload = {
        "prompt": "masterpiece, best quality, colorful and vibrant, landscape, extremely detailed, cozy illustration, illustration, lofi, comforting to look at, a very detailed coffee shop from outside, with a big tree next to it, blue sky, road with pebbles on it, much much detailed, a night scene",  # extra networks also in prompts
        "negative_prompt": "explicit, sensitive, nsfw, low quality, worst quality, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name",
        "seed": -1,
        "steps": 20,
        "width": 1024,
        "height": 1024,
        "cfg_scale": 7,
        "sampler_name": "Euler a",
        "n_iter": 1,
        "batch_size": 1,
    }
    base64Image = sd.call_txt2img_api(**payload)
    print("---------data returned from api---------")
    
    # Decode the base64 image
    image_data = base64.b64decode(base64Image)
    
    # Convert the image data to a BytesIO object
    image_io = BytesIO(image_data)
    
    # Create a zip file in memory
    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('image.png', image_io.getvalue())
    
    zip_io.seek(0)
    
    # Return the zip file as a file response
    data = send_file(zip_io, mimetype='application/zip', as_attachment=True, download_name='image.zip')
    print("---------data returned from api 2---------")
    return data
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
