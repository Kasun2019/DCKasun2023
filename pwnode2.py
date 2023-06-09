from flask import Flask, request, jsonify
from multiprocessing import Value



import threading
import logging
import random

from main import call_announcement, check_election_ongoing, get_details, check_service_work,passwordRead,service_registration, find_port_Id, find_node_id, find_higher_node, election
from bullyInterface import BullyInterface
import time
import sys
import requests


i = Value('i', 0)
app = Flask(__name__)


port_number = int(sys.argv[1])
assert port_number

node_name = sys.argv[2]
assert node_name

logging.basicConfig(filename=f"baseConfig/{node_name}.log", level=logging.INFO)

node_id = find_node_id()
print('Nod ID :', node_id)
bully = BullyInterface(node_name, node_id, port_number)


sr_status = service_registration(node_name, port_number, node_id)


def init(wait=True):
    
    if sr_status == 200:
        ports_of_all_nodes = find_port_Id()
        del ports_of_all_nodes[node_name]
        
      
        node_details = get_details(ports_of_all_nodes)
        
        if wait:
            timeout = random.randint(4, 14)
            time.sleep(timeout)
          

      
        election_ready = check_election_ongoing(ports_of_all_nodes, bully.election, bully.leader)
        if election_ready or not wait:
            print('Election Start: %s' % node_name)
            bully.election = True
            higher_nodes_array = find_higher_node(node_details, node_id)
    
            if len(higher_nodes_array) == 0:
                bully.leader = True
                bully.election = False
                call_announcement(node_name)
                print('Leader is : %s' % node_name)
                passwordRead(node_name)
                print('FINISHED')
            else:
                election(higher_nodes_array, node_id)
    else:
        print('Registration Faild')

timer_ = threading.Timer(15, init)
timer_.start()


@app.route('/findPass',methods=['POST'])
def findPass():
    data = request.get_json()
    enterd_pass = data['password']
    print('Finding the %s psw is'%node_name,enterd_pass)
    with open(r'password_list.txt','r') as fp:
        lines = fp.readlines()
        for row in lines:
            word = enterd_pass
            if row.find(word) != -1:
                print('Yes I am found password by %s !'%node_name)
                return jsonify({'Response': node_name}), 200

        return jsonify({'Response': 'faild'}), 500

@app.route('/response', methods=['POST'])
def response_node():
    data = request.get_json()
    incoming_node_id = data['node_id']
    self_node_id = bully.node_id
    if self_node_id > incoming_node_id:
        threading.Thread(target=init, args=[False]).start()
        bully.election = False
    return jsonify({'Response': 'OK'}), 200

@app.route('/finalAnnouncement',methods=['POST'])
def finalAnnouncement():
    data = request.get_json()
    message = data['message']
    print(message)
    check_leader_active()
    return jsonify({'response': 'OK'}), 200


@app.route('/call_announcement', methods=['POST'])
def announce_coordinator():
    data = request.get_json()
    leader = data['leader']
    bully.leader = leader
    print('Leader is %s ' % leader)
    return jsonify({'response': 'OK'}), 200


@app.route('/nodeDetails', methods=['GET'])
def get_node_details():
    leader_bully = bully.leader
    node_id_bully = bully.node_id
    election_bully = bully.election
    node_name_bully = bully.node_name
    port_number_bully = bully.port
    return jsonify({'node_name': node_name_bully, 'node_id': node_id_bully, 'leader': leader_bully,
                    'election': election_bully, 'port': port_number_bully}), 200


@app.route('/req_pxy', methods=['POST'])
def req_pxy():
    with i.get_lock():
        i.value += 1
        unique_count = i.value

    url = 'http://localhost:%s/response' % port_number
    if unique_count == 1:
        data = request.get_json()
        requests.post(url, json=data)

    return jsonify({'Response': 'OK'}), 200


def check_leader_active():
    threading.Timer(30.0, check_leader_active).start()
    active_leader = check_service_work(bully.leader)
    if active_leader == 'crashed':
        init(False)
    
        




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=port_number)
