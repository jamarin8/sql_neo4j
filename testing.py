from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # Define a simple graph
    graph = {
        "nodes": [
            {"account_id": "1", "label": "Application", "name_dob": "John Doe_1990-01-01", "x": 100, "y": 200},
            {"account_id": "2", "label": "Application", "name_dob": "Jane Doe_1990-02-02", "x": 200, "y": 300},
        ],
        "relationships": [
            {"startNode": "1", "endNode": "2", "type": "LINKED_TO"},
        ]
    }

    # Render the HTML template and pass the graph to it
    return render_template("testing_html.html", graph=graph)

if __name__ == "__main__":
    app.run(debug=True)
