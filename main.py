from datetime import datetime
import json
import requests
import random



def find_node_id():
    date= datetime.utcnow() - datetime(1970, 1, 1)
    seconds =(date.total_seconds())
    milliseconds = round(seconds*1000)
    node_id = milliseconds + random.randint(1, 50000)
    return node_id


#  service registry
def service_registration(name, port, node_id):
    url = "http://localhost:8500/v1/agent/service/register"
    data = {
        "Name": name,
        "ID": str(node_id),
        "port": port,
        "check": {
            "name": "Check in %s" % port,
            "tcp": "localhost:%s" % port,
            "interval": "10s",
            "timeout": "1s"
        }
    }
    put_request = requests.put(url, json=data)
    return put_request.status_code


def check_service_work(service):
    
    url = 'http://localhost:8500/v1/agent/health/service/name/%s' % service
    response = requests.get(url)
    response_content = json.loads(response.text)
    aggregated_state = response_content[0]['AggregatedStatus']
    service_status = aggregated_state
    if response.status_code == 503 and aggregated_state == 'critical':
        service_status = 'crashed'
    
    return service_status



def find_port_Id():
    ports_dict = {}
    response = requests.get('http://127.0.0.1:8500/v1/agent/services')
    nodes = json.loads(response.text)
    for each_service in nodes:
        service = nodes[each_service]['Service']
        status = nodes[each_service]['Port']
        key = service
        value = status
        ports_dict[key] = value
    return ports_dict


def find_higher_node(node_details, node_id):
    node_array = []
    for each in node_details:
        if each['node_id'] > node_id:
            node_array.append(each['port'])
    return node_array


def election(higher_nodes_array, node_id):
    status_code_array = []
    for each_port in higher_nodes_array:
        url = 'http://localhost:%s/req_pxy' % each_port
        data = {
            "node_id": node_id
        }
        post_response = requests.post(url, json=data)
        status_code_array.append(post_response.status_code)
    if 200 in status_code_array:
        return 200



def check_election_ongoing(ports_of_all_nodes, self_election, self_coordinator):
    leader_array = []
    election_array = []
    node_details = get_details(ports_of_all_nodes)

    for each_node in node_details:
        leader_array.append(each_node['leader'])
        election_array.append(each_node['election'])
    leader_array.append(self_coordinator)
    election_array.append(self_election)

    if True in election_array or True in leader_array:
        return False
    else:
        return True



def get_details(ports_of_all_nodes):
    node_details = []
    for each_node in ports_of_all_nodes:
        try:
            url = 'http://localhost:%s/nodeDetails' % ports_of_all_nodes[each_node]
            data = requests.get(url)
            node_details.append(data.json())
        except:
            continue
        
    return node_details


#announce to master
def call_announcement(leader):
    all_nodes = find_port_Id()
    data = {
        'leader': leader
    }
    for each_node in all_nodes:
        url = 'http://localhost:%s/call_announcement' % all_nodes[each_node]
        try:
            requests.post(url, json=data)
        except:
            continue

def finalAnnouncement(message):
    all_nodes = find_port_Id()
    data = {
        'message': message
    }
    for each_node in all_nodes:
        url = 'http://localhost:%s/finalAnnouncement' % all_nodes[each_node]
        requests.post(url, json=data)

def savePassword():
    return input("Enter Password : ")
 

def passwordRead(node_name):
    
    url = 'http://localhost:3001/getPassword'
    try:
        data = requests.get(url)
        passw = data.json()
        
        
        print('password ',passw)
        password = passw
        print('first letter %s ' %password[0])
        fLetter = password[0]
        reCode =0
        sendData = {
            'password': password
        }
        if letter_range('a','e',1,fLetter):
            reCode = callBackPass(sendData,"node 1","3001")
        elif letter_range('e','i',1,fLetter):
            reCode = callBackPass(sendData,"node 2","3002")
        elif letter_range('i','m',1,fLetter):
            reCode = callBackPass(sendData,"node 3","3003")
        elif letter_range('m','r',1,fLetter):
            reCode = callBackPass(sendData,"node 4","3004")
        elif letter_range('r','v',1,fLetter):
            reCode = callBackPass(sendData,"node 5","3005")
        elif letter_range('v','z',1,fLetter):
            reCode = callBackPass(sendData,"node 6","3006")
        else:
            print('invalid password!')
        
        st_code = reCode.status_code
        result = reCode.json()
        nodeName = result['Response']
        if int(st_code) == 200 :
            strMessage = "Pasword Found success by %s :) "%nodeName
            finalAnnouncement(strMessage)
        else:
            strMessage = "Pasword Not Found :( "
            finalAnnouncement(strMessage)
    except:
        reCode = 0


def callBackPass(sendData,nodeNum,portId):
     print('Letter in  range goes to %s'%nodeNum)
     newurl = 'http://localhost:%s/findPass'%portId
     response = requests.post(newurl, json=sendData)
     #st_code = response.status_code
        # result = rd['Response']
     return response

def letter_range(start, stop="{",step=1,fLetter=""):

    for ord_ in list(range(ord(start.lower()),ord(stop.lower()))):
        if fLetter.lower() == chr(ord_):
            return True
     
    return  False
