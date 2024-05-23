import base64
from flask import Flask, request, render_template_string, send_file, jsonify
import automatic1111 as sd
options = {"sd_model_checkpoint":"AnythingXL_xl.safetensors [8421598e93]"}
sd.set_options("sdapi/v1/options", **options)
from io import BytesIO
from collections import deque

app = Flask(__name__)

# Store the last 5 prompts
last_prompts = deque(maxlen=5)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Submit Prompt</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #1a202c;
            color: #cbd5e0;
        }
        .container {
            background-color: #2d3748;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            width: 100%;
        }
        .textarea {
            background-color: #4a5568;
            border: none;
            color: #e2e8f0;
        }
        .button {
            background-color: #3182ce;
            color: #e2e8f0;
        }
        .button:hover {
            background-color: #2b6cb0;
        }
        .spinner {
            border-top-color: #3182ce;
        }
    </style>
</head>
<body class="flex flex-col items-center justify-center min-h-screen w-full">
    <div class="container w-full">
        <form id="promptForm" class="space-y-4">
            <textarea id="promptInput" name="prompt" placeholder="Enter your prompt" class="textarea w-full h-24 p-4 rounded-md text-lg" style="resize: none;"></textarea>
            <div class="text-gray-400 text-sm mt-2">
                <p>Inspiration:</p>
                <ul class="list-disc list-inside">
                    <li>a very detailed coffee shop from outside, with a big tree next to it, blue sky, road with pebbles on it, much much detailed, a night scene</li>
                    <li>A bicycle on a busy road at night</li>
                    <li>sunflower field on a lakeside with blue sky, white clouds and birds, no humans</li>
                </ul>
            </div>
            <div class="text-gray-400 text-sm mt-2">
                <p>Last 5 Prompts:</p>
                <ul id="lastPrompts" class="list-disc list-inside">
                    {% for prompt in last_prompts %}
                        <li>{{ prompt }}</li>
                    {% endfor %}
                </ul>
            </div>
            <button type="submit" class="button w-full py-2 rounded-md text-xl">Submit</button>
        </form>
        <div id="spinner" class="hidden flex justify-center mt-4">
            <div class="spinner border-4 border-t-4 w-9 h-9 rounded-full animate-spin"></div>
        </div>
    </div>
    <div id="responseArea" class="w-full max-w"></div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function() {
            function updateLastPrompts(prompts) {
                var list = $('#lastPrompts');
                list.empty();
                prompts.forEach(function(prompt) {
                    list.append('<li>' + prompt + '</li>');
                });
            }

            $('#promptForm').submit(function(e) {
                e.preventDefault();
                console.log("Form submission started...");
                $('#spinner').removeClass('hidden');
                console.log($('#promptInput').val());

                $.ajax({
                    type: 'POST',
                    url: '/submit',
                    data: JSON.stringify({ prompt: $('#promptInput').val() }),
                    contentType: 'application/json',
                    success: function(response) {
                        console.log("Data received successfully...");
                        console.log(response);
                        var img = $('<img />', { 
                            src: 'data:image/png;base64,' + response.image,
                            alt: 'Generated Image',
                            class: 'w-full rounded-md mt-4'
                        });
                        $('#responseArea').html(img);
                        updateLastPrompts(response.last_prompts);
                        $('#spinner').addClass('hidden');
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.log("Error in form submission: ", textStatus, errorThrown);
                        $('#responseArea').html('<p class="text-red-500">Error in processing your request.</p>');
                        $('#spinner').addClass('hidden');
                    },
                    complete: function() {
                        console.log("Form submission completed.");
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
    return render_template_string(HTML, last_prompts=list(last_prompts))
@app.route("/submit", methods=["POST"])
def submit():
    user_prompt = request.json.get("prompt", "")
    base_prompt = "masterpiece, best quality, colorful and vibrant, landscape, extremely detailed, cozy, illustration, lofi, comforting to look at, "
    final_prompt = ""
    if not user_prompt:
        final_prompt = base_prompt + "a very detailed coffee shop from outside, with a big tree next to it, blue sky, road with pebbles on it, much much detailed, a night scene"
    else:
        final_prompt = base_prompt + user_prompt
    print(final_prompt)
    
    # Store the prompt in the deque
    last_prompts.append(final_prompt)
    
    payload = {
        "prompt": final_prompt,
        "negative_prompt": "humans, explicit, sensitive, nsfw, low quality, worst quality, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name",
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
    
    # Return the image as a base64 string and last prompts as JSON
    image_base64 = base64.b64encode(image_io.getvalue()).decode('utf-8')
    print("---------data returned from api2---------")
    data = jsonify({
        "image": image_base64,
        "last_prompts": list(last_prompts)
    })
    print("---------data returned from api3---------")
    return data 
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
