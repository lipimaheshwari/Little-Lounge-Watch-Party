from flask import Flask, jsonify, request, render_template
from threading import Lock
from time import time
import secrets, string

app = Flask(__name__)
lock = Lock()
rooms = {}
CATALOG = [
    {"title":"Big Buck Bunny","category":"Animation","year":2008,"mood":"Funny","url":"https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4","note":"A cheerful animated short"},
    {"title":"Elephant Dream","category":"Sci-Fi","year":2006,"mood":"Curious","url":"https://storage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4","note":"A surreal little adventure"},
    {"title":"For Bigger Escapes","category":"Adventure","year":2013,"mood":"Adventurous","url":"https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4","note":"A short travel-style clip"},
    {"title":"For Bigger Fun","category":"Comedy","year":2013,"mood":"Funny","url":"https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4","note":"A quick, playful clip"},
]
def stamp():
    return int(time() * 1000)

def make_room(name):
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    rooms[code] = {
        "name": (name or "Little Lounge")[:40], "host": None, "members": {},
        "video": CATALOG[0]["url"], "title": CATALOG[0]["title"],
        "playing": False, "position": 0.0, "updated": stamp(),
        "chat": [], "reactions": [], "playlist": [dict(CATALOG[0])],
        "poll": None, "votes": {}, "event_id": 0
    }
    return code

def room_state(r):
    now = stamp()
    pos = r["position"] + ((now-r["updated"])/1000 if r["playing"] else 0)
    return {"name":r["name"],"host":r["host"],"members":list(r["members"].values()),
            "video":r["video"],"title":r["title"],"playing":r["playing"],"position":max(0,pos),
            "chat":r["chat"][-60:],"reactions":r["reactions"][-20:],
            "playlist":r["playlist"],"poll":r["poll"],"votes":r["votes"],
            "event_id":r["event_id"]}

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/catalog")
def catalog():
    return jsonify(CATALOG)

@app.post("/api/rooms")
def create_room():
    data = request.get_json(silent=True) or {}
    with lock:
        code = make_room(data.get("name"))
        return jsonify({"code":code})

@app.post("/api/rooms/<code>/join")
def join(code):
    data = request.get_json(silent=True) or {}
    user = (data.get("user") or "Guest").strip()[:24] or "Guest"
    with lock:
        r = rooms.get(code.upper())
        if not r: return jsonify({"error":"Room not found. Check the code and try again."}), 404
        # Keep each browser's display name unique enough for this simple local demo.
        if user not in r["members"]:
            r["members"][user] = {"name":user,"joined":stamp()}
        if not r["host"]: r["host"] = user
        return jsonify({"user":user,"state":room_state(r)})

@app.get("/api/rooms/<code>")
def get_room(code):
    with lock:
        r = rooms.get(code.upper())
        if not r: return jsonify({"error":"Room not found. It may have restarted."}), 404
        return jsonify(room_state(r))

@app.post("/api/rooms/<code>/action")
def action(code):
    data = request.get_json(silent=True) or {}
    user = (data.get("user") or "Guest").strip()[:24]
    kind = data.get("kind")
    with lock:
        r = rooms.get(code.upper())
        if not r: return jsonify({"error":"Room not found."}), 404
        if user not in r["members"]:
            r["members"][user] = {"name":user,"joined":stamp()}
            if not r["host"]: r["host"] = user
        is_host = user == r["host"]
        if kind in ("play","pause","seek","video") and not is_host:
            return jsonify({"error":"Only the host can control playback. Ask them to pass the host role to you."}), 403
        now = stamp()
        # Fold elapsed playing time into the saved position before a control change.
        current = r["position"] + ((now-r["updated"])/1000 if r["playing"] else 0)
        if kind == "play":
            r["position"] = current; r["playing"] = True; r["updated"] = now
        elif kind == "pause":
            r["position"] = current; r["playing"] = False; r["updated"] = now
        elif kind == "seek":
            r["position"] = max(0, float(data.get("position",0))); r["updated"] = now
        elif kind == "video":
            item = data.get("item") or {}
            url = item.get("url","")
            if not (url.startswith("https://") or url.startswith("http://")):
                return jsonify({"error":"Please use a valid http(s) video URL."}), 400
            r["video"] = url; r["title"] = (item.get("title") or "Shared video")[:100]
            r["position"] = 0; r["playing"] = False; r["updated"] = now
            if not any(x.get("url")==url for x in r["playlist"]): r["playlist"].append({"title":r["title"],"url":url,"category":"Custom","year":"—","mood":"Your pick","note":"Added by the host"})
        elif kind == "chat":
            msg = (data.get("message") or "").strip()[:240]
            if msg: r["chat"].append({"user":user,"message":msg,"at":now})
            r["chat"] = r["chat"][-60:]
        elif kind == "reaction":
            emoji = data.get("emoji","✨")
            if emoji not in ["💗","😂","👏","✨","😮"]: emoji = "✨"
            r["reactions"].append({"user":user,"emoji":emoji,"at":now})
            r["reactions"] = r["reactions"][-20:]
        elif kind == "add":
            item = data.get("item") or {}
            if item.get("url") and not any(x.get("url")==item["url"] for x in r["playlist"]):
                r["playlist"].append(item)
        elif kind == "vote":
            if r["poll"] and data.get("option") in r["poll"]["options"]:
                r["votes"][user] = data["option"]
        elif kind == "poll":
            question = (data.get("question") or "What next?").strip()[:100]
            opts = [str(x).strip()[:50] for x in data.get("options",[]) if str(x).strip()][:4]
            if len(opts) >= 2: r["poll"]={"question":question,"options":opts,"by":user}; r["votes"]={}
        elif kind == "host":
            target = data.get("target")
            if is_host and target in r["members"]: r["host"] = target
        elif kind == "leave":
            r["members"].pop(user,None)
            if r["host"] == user:
                r["host"] = next(iter(r["members"]),None)
        r["event_id"] += 1
        return jsonify(room_state(r))

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
