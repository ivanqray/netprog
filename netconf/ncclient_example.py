'''
Example for using filter into ncclient module;
'''
>>>>>>> linkoln
from ncclient import manager
import xmltodict
from xml.dom.minidom import pasrer, ParseString
import json

filt = '''<filter>
            <routing xmlns="urn:ietf:params:xml:ns:yang:ietf-routing">
            </routing>
        </filter>'''
with manager.connect(host = 'ios-xe-mgmt.cisco.com',
		      port = '10000',
		      username = 'developer',
		      password = 'C1sco12345',
		      hostkey_verify = False,
              device_params={'name':'nexus'}) as m:
              outp = m.get(filt)
              res = xmltodict.parse(outp.xml)
              itogo = res['rpc-reply']['data']
              defvrf = itogo['routing']['routing-instance']

              rr = defvrf[1]['routing-protocols']['routing-protocol']
              destpfx = rr[1]['static-routes']['ipv4']['route']['destination-prefix']
              out_int = rr[1]['static-routes']['ipv4']['route']['next-hop']['outgoing-interface']
              print(f'route {destpfx} through interface {out_int}'req)
