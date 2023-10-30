from flask import Flask, request, jsonify
import pandas as pd
import pickle
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/movies": {"origins": "http://localhost:3000"}})

class APIAuthError(Exception):
  code = 403
  description = "Authentication Error"

@app.route("/movies", methods=["POST"])
def helloWorld():
    movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open("similarity.pkl", "rb"))
    movie_name = request.json["movie_name"]
    movie_index = movies[movies["title"] == movie_name].index
    if len(movie_index) == 0:
        return {"code": 404, "message": "I have limited data, I can't recommend any movie for you!"}, 404
    distances = similarity[movie_index[0]]
    movies_list = sorted(list(enumerate(distances)),
                         reverse=True, key=lambda x: x[1])[1:6]
    recommended = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id.item()
        response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=c4f00a75ca81ffc8a72eec01038b8ec6&append_to_response=videos".format(movie_id))
        data = response.json()
        recommended.append(data)
    return jsonify({"code": 200, "results": recommended}), 200


if __name__ == "__main__":
    app.run(debug=True)
