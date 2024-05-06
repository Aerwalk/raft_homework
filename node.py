import argparse
import threading
import time
from flask import Flask, request, render_template
import logging

from consensus import ConsensusManager

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--init_value', dest='init_value', default="25")
parser.add_argument('-p', '--my_http_port', dest='my_http_port', required=True)
parser.add_argument('-m', '--my_raft_port', dest='my_raft_port', required=True)
parser.add_argument('-o', '--others_raft_port', dest='others_raft_port', nargs="+", required=True)

params = parser.parse_args()

print("* start node", params.my_raft_port, "with init value", int(params.init_value))
print("* others are:", " ".join(params.others_raft_port))

consensus_manager = ConsensusManager(int(params.init_value), params.my_raft_port, params.others_raft_port)
consensus_manager.start()
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, template_folder='.')


@app.route('/', methods=['GET'])
def dashboard():
    value = consensus_manager.get()
    logging.info("Received GET request for dashboard with value: %s", value)
    return render_template('node.html', value=value)

@app.route('/append_entries', methods=['POST'])
def handle_append_entries():
    data = request.get_json()
    action = data.get('action')
    value = data.get('value')
    if action == "add":
        consensus_manager.add(value)
    elif action == "sub":
        consensus_manager.sub(value)
    elif action == "mul":
        consensus_manager.mul(value)
    else:
        print("Недопустимое действие в RPC AppendEntries")
@app.route('/get', methods=['GET'])
def get_data():
    value = consensus_manager.get()
    return str(value)


@app.route('/add', methods=['POST'])
def add_data():
    value = int(request.form['value'])
    consensus_manager.add(value)
    return "commited"


@app.route('/sub', methods=['POST'])
def sub_data():
    value = int(request.form['value'])
    consensus_manager.sub(value)
    return "commited"


@app.route('/mul', methods=['POST'])
def mul_data():
    value = int(request.form['value'])
    consensus_manager.mul(value)
    return "commited"


@app.route('/get_status', methods=['GET'])
def get_status():
    return str(consensus_manager.get_status())


if __name__ == "__main__":
    # Disable Flask logs!
    import logging
    log = logging.getLogger('werkzeug')
    log.disabled = True

    app.run(debug=True, port=params.my_http_port)