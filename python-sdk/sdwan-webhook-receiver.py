from flask import Flask, request

app = Flask(__name__)

@app.route("/api/notifications", methods=["POST"])
def notify():
    data = request.get_json(force=True)
    print(data)
    return {"result": "Notification received and processed"}

if __name__=="__main__":
    app.run()