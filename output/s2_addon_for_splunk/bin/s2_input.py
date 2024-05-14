import import_declare_test

import sys
import json

from splunklib import modularinput as smi

import os
import traceback
import requests
from splunklib import modularinput as smi
from solnlib import conf_manager
from solnlib import log
from solnlib.modular_input import checkpointer
from splunktaucclib.modinput_wrapper import base_modinput  as base_mi 

import requests

import xml.etree.ElementTree as ET

bin_dir  = os.path.basename(__file__)
app_name = os.path.basename(os.path.dirname(os.getcwd()))

class ModInputS2_INPUT(base_mi.BaseModInput): 

    def __init__(self):
        use_single_instance = False
        super(ModInputS2_INPUT, self).__init__(app_name, "s2_input", use_single_instance) 
        self.global_checkbox_fields = None

    def get_scheme(self):
        scheme = smi.Scheme('s2_input')
        scheme.description = 's2_input'
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False

        scheme.add_argument(
            smi.Argument(
                'name',
                title='Name',
                description='Name',
                required_on_create=True
            )
        )
        scheme.add_argument(
            smi.Argument(
                'account',
                required_on_create=True,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'Server_URL',
                required_on_create=True,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'Username',
                required_on_create=True,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'Password',
                required_on_create=True,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'SessionId',
                required_on_create=False,
            )
        )
        
        return scheme

    def validate_input(self, definition):
        """validate the input stanza"""
        """Implement your own validation logic to validate the input stanza configurations"""
        pass

    def get_app_name(self):
        return "app_name" 

    def collect_events(helper, ew):

        index=helper.get_arg("index")
        url = "http://{{Server_URL}}/appdevent/nbapi/event"
        sessionid_url = "http://{{Server_URL}}/appdevent/nbapi/sessionid"

        # insert input values into the url and/or header (helper class handles credential store)
        opt_SessionId = ""
        opt_Server_URL = helper.get_arg('Server_URL')
        opt_Username = helper.get_arg('Username')
        opt_Password = helper.get_arg('Password')
        opt_SessionId = helper.get_arg('SessionId')

        helper.log_info("\n\n [INFO] Settings for the "+opt_Server_URL+" : ["+opt_Username+":"+opt_Password+"] \n\n")

        if(opt_SessionId != ""):
            helper.log_info("\n\n [INFO] SessionId for the Add-on : ["+opt_SessionId+"] \n\n")

            #FIXME:
            url = url.replace("{{"+'Server_URL'+"}}",opt_Server_URL)
            url = "http://192.168.204.50/appdevent/nbapi/event"

            cookies = {
                '.sessionId': opt_SessionId
            }

            headers = {
                'Content-Type': 'text/xml',
            }

            payload = """
            <NETBOX-API>
                <COMMAND name='StreamEvents'>
                    <PARAMS>
                        <TAGNAMES>
                            <PERSONID />
                            <PERSONNAME />
                            <ACNAME />
                            <ACTIVITYID />
                            <CDT />
                            <DESCNAME />
                        </TAGNAMES>
                    </PARAMS>
                </COMMAND>
            </NETBOX-API>
            """

            try:
                # Now execute the api call with the SessionId

                #response = helper.send_http_request(url, "POST", headers=headers, payload=payload, cookies=cookies, use_proxy=True)
                response = requests.post(url, headers=headers, data=payload, cookies=cookies)

                try:
                    helper.log_info ("\n\n [INFO] ("+response.status_code+") "+response.text+" [Username : "+opt_Username+"] \n\n")
                    response.raise_for_status()
                    
                except Exception as e:
                    helper.log_error ("\n\n [ERROR] "+response.text+" "+str(e)+" [Username : "+opt_Username+"] \n\n")
                
                if (response.status_code == 200):

                    try:
                        #data = json.dumps(response.json())
                        data=response.content.decode('utf-8')

                        sourcetype=  opt_Username  + "://" + opt_Server_URL
                        event = helper.new_event(source=opt_Username, index=index, sourcetype=sourcetype , data=data)
                        helper.log_info("\n\n [INFO] Event to insert in XML format. \n source="+opt_Username+", index="+index+", sourcetype="+opt_Server_URL+" , data="+str(data)+" [Username : "+opt_Username+"] \n\n")
                        ew.write_event(event)
                        helper.log_info("\n\n [INFO] Event Inserted in XML format. \n source="+opt_Username+", index="+index+", sourcetype="+opt_Server_URL+" , data="+str(data)+" [Username : "+opt_Username+"] \n\n")
                    except Exception as e:
                        helper.log_error("\n\n [ERROR] Error inserting XML event. : "+str(e)+" [Username : "+opt_Username+"] \n\n")

                else:
                    helper.log_info("\n\n [INFO] response.status_code = "+str(response.status_code)+" [Username : "+opt_Username+"] \n\n")               
            except Exception as e:
                helper.log_error("\n\n [ERROR] Error using SessionId. : "+str(e)+" [Username : "+opt_Username+"] \n\n")

        else:
            helper.log_info("\n\n [INFO] No SessionId found in the Input : ["+opt_SessionId+"] \n\n")

            #FIXME:
            sessionid_url = sessionid_url.replace("{{"+'Server_URL'+"}}",opt_Server_URL)
            sessionid_url = 'http://172.23.204.50/goforms/nbapi'

            headers = {
                #"User-Agent": "curl/8.1.2",
                "Accept": "*/*",
                "Content-Type": "application/xml"
            }
            cookies = None

            # Define the XML data (payload)
            payload = '''
            <NETBOX-API>
                <COMMAND name="Login" num="1" dateformat="tzoffset">
                    <PARAMS>
                        <USERNAME>{{Username}}</USERNAME>
                        <PASSWORD>{{Password}}</PASSWORD>
                    </PARAMS>
                </COMMAND>
            </NETBOX-API>
            '''

            try:
                # Now execute the api call if no SessionId is provided.

                #response = helper.send_http_request(sessionid_url, "POST", headers=headers, payload=payload, cookies=cookies, verify=True, use_proxy=True)
                response = requests.post(sessionid_url, headers=headers, data=payload)

                try:
                    helper.log_info ("\n\n [INFO] ("+response.status_code+") "+response.text+" [Username : "+opt_Username+"] \n\n")
                    response.raise_for_status()
                    
                except Exception as e:
                    helper.log_error ("\n\n [ERROR] "+response.text+" "+str(e)+" [Username : "+opt_Username+"] \n\n")

                if response.status_code == 200:
                    try:
                        #data = json.dumps(response.json())
                        data = response.content.decode('utf-8')

                        helper.log_info("\n\n [INFO] Response to search for the SessionId. data="+str(data)+" [Username : "+opt_Username+"] \n\n")

                        try:
                            '''
                            # here edit find the <SessionId>
                            tag_start = "<SessionId>"
                            tag_end = "</SessionId>"
                            pattern = f'{re.escape(tag_start)}(.*?)\s*{re.escape(tag_end)}'
                            SessionId = re.search(pattern, data)
                            '''

                            root = ET.fromstring(data)
                            SessionId = root.attrib.get('sessionid')

                            if(SessionId):
                                opt_SessionId = SessionId
                                helper.log_info("\n\n [INFO] SessionId for the Add-on : ["+opt_SessionId+"] \n\n")

                                url = url.replace("{{"+'Server_URL'+"}}",opt_Server_URL)

                                cookies = {".sessionId": opt_SessionId}

                                headers = {"Content-Type": "application/xml"}

                                try:
                                    # Now execute the api call with the SessionId

                                    response = helper.send_http_request(url, "GET", headers=headers,  parameters="", payload=None, cookies=cookies, verify=True, cert=None, timeout=None, use_proxy=True)

                                    try:
                                        response.raise_for_status()
                                        
                                    except Exception as e:
                                        helper.log_error ("\n\n [ERROR] "+response.text+" "+str(e)+" [Username : "+opt_Username+"] \n\n")
                                    
                                    if (response.status_code == 200):

                                        try:
                                            #data = json.dumps(response.json())
                                            data = response.content.decode('utf-8')
                                            
                                            sourcetype=  opt_Username  + "://" + opt_Server_URL
                                            event = helper.new_event(source=opt_Username, index=index, sourcetype=sourcetype , data=data)
                                            helper.log_info("\n\n [INFO] Event to insert in XML format. \n source="+opt_Username+", index="+index+", sourcetype="+opt_Server_URL+" , data="+str(data)+" [Username : "+opt_Username+"] \n\n")
                                            ew.write_event(event)
                                            helper.log_info("\n\n [INFO] Event Inserted in XML format. \n source="+opt_Username+", index="+index+", sourcetype="+opt_Server_URL+" , data="+str(data)+" [Username : "+opt_Username+"] \n\n")
                                        except Exception as e:
                                            helper.log_error("\n\n [ERROR] Error inserting XML event. : "+str(e)+" [Username : "+opt_Username+"] \n\n")

                                    else:
                                        helper.log_info("\n\n [INFO] response.status_code = "+str(response.status_code)+" [Username : "+opt_Username+"] \n\n")               
                                except Exception as e:
                                    helper.log_error("\n\n [ERROR] Error using SessionId. : "+str(e)+" [Username : "+opt_Username+"] \n\n")


                        except Exception as e:
                            helper.log_error("\n\n [ERROR] Error using SessionId. : "+str(e)+"  [Username : "+opt_Username+"] \n\n")
                    except Exception as e:
                        helper.log_error("\n\n [ERROR] Error finding SessionId  : "+str(e)+" [Username : "+opt_Username+"] \n\n")
                else:
                    helper.log_info("\n\n [INFO] response.status_code = "+str(response.status_code)+" [Username : "+opt_Username+"] \n\n")
            except Exception as e:
                helper.log_error ("\n\n [ERROR] When executing the api call to get SessionId. : "+str(e)+" [Username : "+opt_Username+"] \n\n")

    def get_account_fields(self):
        account_fields = []
        return account_fields

    def get_checkbox_fields(self):
        checkbox_fields = []
        return checkbox_fields

    def get_global_checkbox_fields(self):
        if self.global_checkbox_fields is None:
            checkbox_name_file = os.path.join(bin_dir, 'global_checkbox_param.json')
            try:
                if os.path.isfile(checkbox_name_file):
                    with open(checkbox_name_file, 'r') as fp:
                        self.global_checkbox_fields = json.load(fp)
                else:
                    self.global_checkbox_fields = []
            except Exception as e:
                self.log_error('Get exception when loading global checkbox parameter names. ' + str(e))
                self.global_checkbox_fields = []
        return self.global_checkbox_fields

if __name__ == '__main__':
    exit_code = ModInputS2_INPUT().run(sys.argv)
    sys.exit(exit_code)


