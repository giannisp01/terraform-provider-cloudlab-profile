"""An example of constructing a profile with node IP addresses specified
manually.

Instructions:
Wait for the profile instance to start, and then log in to either VM via the
ssh ports specified below.  (Note that even though the EXPERIMENTAL
data plane interfaces will use the addresses given in the profile, you
will still connect over the control plane interfaces using addresses
given by the testbed.  The data plane addresses are for intra-experiment
communication only.)
"""

import geni.portal as portal
import geni.rspec.pg as rspec

# Create a portal context, needed to defined parameters
pc = portal.Context()

"""
Define User Parameters
"""
pc.defineParameter("IPv4", "Node IPv4 address", portal.ParameterType.STRING, "")
pc.defineParameter("SubnetMask", "Node subnet mask", portal.ParameterType.STRING, "")
pc.defineParameter("VLAN", "Node VLAN", portal.ParameterType.STRING, "")


pc.verifyParameters()

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()

request = pc.makeRequestRSpec()

node1 = request.XenVM("node1")
iface1 = node1.addInterface("if1")

# Specify the component id and the IPv4 address
iface1.component_id = "eth1"
iface1.addAddress(rspec.IPv4Address(params.IPv4, params.SubnetMask))

link = request.Link("link")
link.addInterface(iface1)

# Specify the name of the shared vlan. This vlan is special in that it has
# been setup in advance by system administrators on a specific cluster.
link.shared_vlan = params.VLAN

pc.printRequestRSpec(request)
