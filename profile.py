# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the InstaGENI library.
import geni.rspec.igext as ig
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal object,
pc = portal.Context()

agglist = [
    ("urn:publicid:IDN+emulab.net+authority+cm", "emulab.net"),
    ("urn:publicid:IDN+utah.cloudlab.us+authority+cm", "utah.cloudlab.us"),
    ("urn:publicid:IDN+clemson.cloudlab.us+authority+cm", "clemson.cloudlab.us"),
    ("urn:publicid:IDN+wisc.cloudlab.us+authority+cm", "wisc.cloudlab.us"),
    ("urn:publicid:IDN+apt.emulab.net+authority+cm", "apt.emulab.net"),
    ("", "Any")
]

pc.defineParameter(
    "aggregate","Specific Aggregate",portal.ParameterType.STRING,
    "urn:publicid:IDN+emulab.net+authority+cm",agglist)
pc.defineParameter(
    "image","Node Image",portal.ParameterType.STRING,
    'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD',
    longDescription="The image your node will run.")
pc.defineParameter(
    "routableIP","Routable IP",
    portal.ParameterType.BOOLEAN,False,
    longDescription="Add a routable IP to the VM.")


pc.defineParameter(
    "createConnectableSharedVlan", "Create Connectable Shared VLAN",
    portal.ParameterType.BOOLEAN, False,
    longDescription="Create a placeholder, connectable shared VLAN stub and 'attach' the first node to it.  You can "
                    "use this during the experiment to connect this experiment interface to another experiment's "
                    "shared VLAN."),
pc.defineParameter(
    "createSharedVlan", "Create Shared VLAN",
    portal.ParameterType.BOOLEAN, True,
    longDescription="Create a new shared VLAN with the name above, and connect the first node to it."),
pc.defineParameter(
    "connectSharedVlan", "Connect to Shared VLAN",
    portal.ParameterType.BOOLEAN, False,
    longDescription="Connect an existing shared VLAN with the name below to the first node."),
pc.defineParameter(
    "sharedVlanName", "Shared VLAN Name",
    portal.ParameterType.STRING, "",
    longDescription="A shared VLAN name (functions as a private key allowing other experiments to connect to this "
                    "node/VLAN), used when the 'Create Shared VLAN' or 'Connect to Shared VLAN' options above are "
                    "selected.  Must be fewer than 32 alphanumeric characters."),
pc.defineParameter(
    "sharedVlanAddress", "Shared VLAN IP Address",
    portal.ParameterType.STRING, "10.254.254.1",
    longDescription="Set the IP address for the shared VLAN interface.  Make sure to use an unused address within the "
                    "subnet of an existing shared vlan!"),
pc.defineParameter(
    "sharedVlanNetmask", "Shared VLAN Netmask",
    portal.ParameterType.STRING, "255.255.255.0",
    longDescription="Set the subnet mask for the shared VLAN interface, as a dotted quad.")

params = pc.bindParameters()

n = 0
if params.createConnectableSharedVlan:
    n += 1
if params.createSharedVlan:
    n += 1
if params.connectSharedVlan:
    n += 1
if n > 1:
    err = portal.ParameterError(
        "Must choose only a single shared vlan operation (create, connect, create connectable)",
        ['createConnectableSharedVlan',
         'createSharedVlan',
         'connectSharedVlan'])
    pc.reportError(err)
if n == 0:
    err = portal.ParameterError(
        "Must choose one of the shared vlan operations: create, connect, create connectable",
        ['createConnectableSharedVlan',
         'createSharedVlan',
         'connectSharedVlan'])
    pc.reportError(err)

pc.verifyParameters()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

tour = ig.Tour()
tour.Description(ig.Tour.TEXT, "Create a vlan.")
request.addTour(tour)


node = ig.XenVM("node-0")
node.exclusive = False
if params.routableIP:
    node.routable_control_ip = True
if params.aggregate:
    node.component_manager_id = params.aggregate
if params.image:
    node.disk_image = params.image
iface = node.addInterface("ifSharedVlan")
if params.sharedVlanAddress:
    iface.addAddress(
        pg.IPv4Address(params.sharedVlanAddress, params.sharedVlanNetmask))
sharedvlan = pg.Link('shared-vlan')
sharedvlan.addInterface(iface)
#sharedvlan.enableSharedVlan()
sharedvlan.createSharedVlan(params.sharedVlanName)
sharedvlan.connectSharedVlan(params.sharedVlanName)
sharedvlan.link_multiplexing = True
sharedvlan.best_effort = True

request.addResource(node)
request.addResource(sharedvlan)

pc.printRequestRSpec(request)