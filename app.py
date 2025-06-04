from flask import Flask, render_template, request, redirect, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

app = Flask(__name__)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        visibility = request.form["visibility"]
        made_for_kids = request.form["made_for_kids"]
        video_file = request.files["video"]

        filepath = os.path.join("uploads", video_file.filename)
        video_file.save(filepath)

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        youtube = build("youtube", "v3", credentials=creds)

        request_body = {
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": visibility,
                "madeForKids": made_for_kids == "yes"
            }
        }

        media = MediaFileUpload(filepath, mimetype="video/mp4", resumable=True)
        upload_request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
        upload_request.execute()

        return jsonify({"status": "success", "message": "Video uploaded!"})

    return render_template("upload.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

