"""
Given network interfaces and corresponding destination IPs.
"""
import os
import subprocess
import time

class NRoute:
    def __init__(self, iface, destination, prio=None):
        self.iface = iface
        self.destination = destination
        self.prio = prio

    def eval(self):
        try:
            response = subprocess.check_output(
                ['ping', '-W', '1', '-c', '1', '-I', self.iface, self.destination],
                stderr=subprocess.STDOUT,  # get all output
                universal_newlines=True  # return string not bytes
            )
        except subprocess.CalledProcessError:
            print ('PING ERROR')
            response = None
        
        if response is None:
            return False
        
        ping_success = response.find('1 packets transmitted, 1 received, 0% packet loss, time 0ms')
        if ping_success < 0:
            return False

        return True


    def ip_sanity_check(self, ip):
        res = ip.split('.')
        return any([r.isdigit() for r in res]) & (len(res) == 4)

    def iface_ip(self):
        query = "ip addr show "+ self.iface +" | grep 'inet\\b' | awk '{print $2}' | cut -d/ -f1"
        ip = subprocess.check_output(query, shell=True).rstrip().decode('UTF-8')
        if ip == '':
            return None

        return ip

    def equal(self, other):
        if (self.iface == other.iface) and (self.destination == other.destination):
            return True

        return False

    def conflict(self, other):
        if (self.destination == other.destination) and (self.iface != other.iface):
            return True
        return False

class NRouter:
    def __init__(self, destination):
        self.destination = destination # The destination to comm to e.g. 172.16.2.1
        self.routes = []

    def add_route(self, nroute):
        self.routes.append(nroute)

    def run(self):
        # Choose active route, if multiple use route with highest prio

        print (' ----------- RUN ----------')

        while True:
            route = None
            for nr in self.routes:
                if(nr.eval()):
                    if not route is None:
                        #check if higher prio
                        if nr.prio > route.prio:
                            route = nr
                    else:
                        route = nr


            print ('  WINNING route ', route.iface, ' ', route.destination)

            # Adept routing table
            rt = RoutingTable()
            rt.update(NRoute(route.iface, self.destination))

            time.sleep(1)

class RoutingTable:
    def __init__(self):
        self.routes = []
        self.parse()

    def parse_line(self, line):
        dest, gw, genmask, flags, metric, ref, use, iface = line.split()
        self.routes.append(NRoute(iface, dest))

    def parse(self):
        output = subprocess.check_output("route -n", shell=True)
        lines = output.splitlines()

        for i, l in enumerate(lines):
            if i == 0:
                continue
            self.parse_line(l.decode('UTF-8'))

    def remove_route(self, route):
        print ('  REMOVING route ', route.iface, ' ', route.destination)
        output = subprocess.check_output("sudo /usr/sbin/route del "+ route.destination +" dev "+ route.iface, shell=True)

    def resolve_conflict(self, route):
        # Remove all routes which have the same destination, but another interface
        for r in self.routes:
            if r.conflict(route):
                print ('conflict found')
                self.remove_route(r)

    def update(self, route):

        #skip if route exists
        for r in self.routes:
            if r.equal(route):
                return

        #Erase an existing route if conflicting with new route
        self.resolve_conflict(route)

        #Add new route
        print ('  ADDING route ', route.iface, ' ', route.destination)
        output = subprocess.check_output("sudo /usr/sbin/route add -host "+ route.destination +" dev "+ route.iface, shell=True)


#Test
if __name__ == "__main__":
    
    nrouter = NRouter(destination='172.16.2.1') #Initializing the router with the target route. From iface we want to comm with destination
    nrouter.add_route(NRoute('enp0s31f6', '192.168.68.106', 100)) #As a hint. Our target route might be reached wia interface and has this destination
    nrouter.add_route(NRoute('tun0', '10.8.0.21', 1)) #Another hint

    nrouter.run()
    