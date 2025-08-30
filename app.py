from flask import Flask, jsonify,request
from flask_cors import CORS

import io
import whisper
import os
import json
from pydub import AudioSegment
from google import genai
import datetime

usemodel = model = whisper.load_model("base")
geminiprompt = """You will be given a single-sentence description of a programming problem, similar to what might appear on a competitive coding platform like LeetCode. Your task is to generate a diverse set of test cases for a function that would solve this problem.
In case the problem statement cannot be understood or is unintelligible , try to infer a problem statement similar to it and generate testcase for it

For each problem description, you should:


Implicitly Infer Constraints: Based on the nature of the problem described, make reasonable assumptions about the potential constraints on the input size, data types, and value ranges. Consider common constraints seen in similar types of problems. Briefly note the constraints you've inferred for each problem.

Generate Diverse Test Cases: Create a variety of test cases that cover:

Basic Cases: Typical, straightforward inputs along with expected outputs.
Edge Cases: Inputs that are at the boundaries of the inferred constraints (e.g., minimum/maximum size, smallest/largest values).
Empty/Null Cases: If the problem description allows for empty or null inputs.
Single Element Cases: If the input is a collection, consider cases with only one element.
Duplicate Element Cases: If the input can contain duplicates.
Negative/Zero Cases: If the input can involve negative numbers or zero.
Performance-Sensitive Cases (if implied): For problems that might have performance implications (e.g., involving large collections), include at least one test case with a significantly larger input size based on your inferred constraints.
Format the Output: Show the test cases in formatted in latex with each request in a new line. do not give inferred constraints.

You are not to return anything but the test cases generated.

Example Problem Description:

"Given a list of integers, find the largest sum of a contiguous subarray."

Current Problem Description:

"""
transcribedtext = ""
geminiresult = ""

#alternatively known as "savemylife" library

#also glossed over the entire generate_waveform function

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes



@app.route('/',methods=['GET'])
def defaultgreeting():
    return ("This is the home page : Enter a route to continue")

@app.route('/end/getjson', methods=['GET'])
def getjson():
    return jsonify({"message": "Json Hello from Flask backend!"})

@app.route('/end/getstring',methods=['GET'])
def getstring():
    data = "Empty string from backend"
    return data


@app.route('/end/poststring',methods=['POST'])
def poststring():
    data = request.get_json()
    message = data.get('message','Frontend data invalid')
    return (f"Recieved {message} successfully")
    
    
@app.route('/end/upload-audio',methods= ['POST'])
def process_audio():
    global usemodel
    global transcribedtext
    global geminiprompt
    if 'file' not in request.files:
        return jsonify({'error' : "No file provided"}), 400

    file = request.files['file']
    print("Recieved File:", file.filename)
    print("Content-type:",file.content_type)
    
    try:
        model = usemodel
        # Load Whisper Model (Tiny, Base, Small, Medium, Large available)

        #Converting webm to wav before processing
        audio = AudioSegment.from_file(file,format="webm")
        wav_io = io.BytesIO()
        audio.export(wav_io,format="wav")
        wav_io.seek(0)
        res = webm_audio_to_text(wav_io,model)
        transcribedtext = ""
        print("This is what we got",res)
        transcribedtext = res
        geminiprompt = geminiprompt + transcribedtext
        print("Gemini will get",geminiprompt)
        return jsonify({'key' : res})
    except Exception as e:
        return (f'Processing error {e}')

def webm_audio_to_text(wav_io,model):
    with open("temp.wav","wb") as f:
        f.write(wav_io.read())
    
    result = model.transcribe("temp.wav")

    return result["text"]        


@app.route("/end/geminiaccess",methods=['GET'])       
def testcases():
    global geminiresult
    from google import genai
    global geminiprompt
    client = genai.Client(api_key="")
    response = client.models.generate_content(
        model="gemini-1.5-flash", contents=geminiprompt
    )
    geminiresult = response.text
    timetest()
    return jsonify({"text": response.text})

def timetest():
    global geminiresult 
    global transcribedtext
    global geminiprompt 
    now = datetime.datetime.now()
    print("fuck")
    f = open("GeminiLog.txt","a")
    f.write(f"\n<<<< AT {now} >>>>\n")
    f.write("\n\nPrompt: \n")
    f.write(transcribedtext)
    f.write("\n\nResult: \n")
    f.write(geminiresult)
    f.write("\n ------------  \n ----------- \n\n\n  ")
    return jsonify({'key' : now})

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Run on port 5000 (adjust if needed)
    
