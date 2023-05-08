class BullyInterface:

    def __init__(self, node_name, node_id, port_number, election=False, leader=False):
        self.node_name = node_name
        self.node_id = node_id
        self.port = port_number
        self.election = election
        self.leader = leader


