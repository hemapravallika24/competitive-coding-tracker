from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import os

app = Flask(__name__)

# ✅ Production-ready: get Mongo URI from environment or fallback to local
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://hemapravallika24:Hemapravallika@codingtracker-cluster.2mcgbum.mongodb.net/coding_tracker?retryWrites=true&w=majority&appName=codingtracker-cluster"
)

try:
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    client.admin.command("ping")
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print("❌ MongoDB connection error:", e)
    exit(1)

db = client["coding_tracker"]
progress_collection = db["progress"]

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main page: displays form to enter daily coding progress.
    """
    if request.method == "POST":
        try:
            date = datetime.strptime(request.form["date"], "%Y-%m-%d")
            problems_solved = int(request.form["problems_solved"])
            easy = int(request.form["easy"])
            medium = int(request.form["medium"])
            hard = int(request.form["hard"])

            progress = {
                "date": date,
                "problems_solved": problems_solved,
                "easy": easy,
                "medium": medium,
                "hard": hard
            }

            progress_collection.insert_one(progress)
            print(f"✅ Progress added: {progress}")
            return redirect(url_for("dashboard"))

        except Exception as e:
            print("❌ Error adding progress:", e)
            return "Error adding progress. Please check your inputs.", 400

    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    """
    Dashboard page: shows charts of coding progress over time.
    """
    try:
        progress = list(progress_collection.find().sort("date", 1))
        if progress:
            dates = [p["date"].strftime("%Y-%m-%d") for p in progress]
            problems = [p["problems_solved"] for p in progress]
            easy = [p["easy"] for p in progress]
            medium = [p["medium"] for p in progress]
            hard = [p["hard"] for p in progress]
        else:
            dates, problems, easy, medium, hard = [], [], [], [], []

        return render_template(
            "dashboard.html",
            dates=dates,
            problems=problems,
            easy=easy,
            medium=medium,
            hard=hard
        )

    except Exception as e:
        print("❌ Error loading dashboard:", e)
        return "Error loading dashboard.", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
