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

import xml.etree.ElementTree as ET
import json

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
        
        return scheme

    def validate_input(self, definition):
        """validate the input stanza"""
        """Implement your own validation logic to validate the input stanza configurations"""
        pass

    def get_app_name(self):
        return "app_name" 

    def collect_events(helper, ew):

        Username = helper.get_arg("Username")
        password = helper.get_arg("Password")
        url = helper.get_arg("Server_URL")
        helper.log_info("\n\n [INFO] Settings for the Add-on : ["+Username+":"+password+"@"+url+"] \n\n")

        # insert input values into the url and/or header (helper class handles credential store)
        opt_account = helper.get_arg('account')
        url = url.replace("{{"+'account'+"}}",opt_account)
        headers = headers.replace("{{"+'account'+"}}",opt_account)
        
        opt_Server_URL = helper.get_arg('Server_URL')
        url = url.replace("{{"+'Server_URL'+"}}",opt_Server_URL)
        headers = headers.replace("{{"+'Server_URL'+"}}",opt_Server_URL)
        
        opt_Username = helper.get_arg('Username')
        url = url.replace("{{"+'Username'+"}}",opt_Username)
        headers = headers.replace("{{"+'Username'+"}}",opt_Username)
        
        opt_Password = helper.get_arg('Password')
        url = url.replace("{{"+'Password'+"}}",opt_Password)
        headers = headers.replace("{{"+'Password'+"}}",opt_Password)
        
        # Now execute the api call
        headers=json.loads(headers)
        response = helper.send_http_request(url, "GET", headers=headers,  parameters="", payload=None, cookies=None, verify=True, cert=None, timeout=None, use_proxy=True)

        try:
            response.raise_for_status()
            
        except:
            helper.log_error ("\n\n [ERROR] "+response.text+"[Username : "+Username+"] \n\n")
        
        if response.status_code == 200:
            try:
                data = json.dumps(response.json())
                sourcetype=  "s2_input"  + "://" + helper.get_input_stanza_names()
                event = helper.new_event(source="s2_input", index=helper.get_output_index(), sourcetype=sourcetype , data=data)
                ew.write_event(event)
            except:
                helper.log_error("\n\n [ERROR] Error inserting event [Username : "+Username+"] \n\n")
                
            #An event came, write that to an Index.
            helper.log_info(f"\n\n [INFO] No match_VsUUID and match_SessionId. [Username : "+Username+"] \n\n")
            helper.log_info(f"\n\n [INFO] Data to write to an Index: \n {data} \n [Username : "+Username+"] \n\n")

            # get input values
            index=helper.get_arg("index")
            account=helper.get_arg("account")['name']

            try:
                root = ET.fromstring(data)
                def xml_to_dict(item):
                    if len(item) == 0:
                        return item.text
                    result = {}
                    for i in item:
                        i_data = xml_to_dict(i)
                        if i.tag in result:
                            if type(result[i.tag]) is list:
                                result[i.tag].append(i_data)
                            else:
                                result[i.tag] = [result[i.tag], i_data]
                        else:
                            result[i.tag] = i_data
                    return result
                xml_dict = {root.tag: xml_to_dict(root)}
                # Convert the Python dictionary to JSON
                json_data = json.dumps(xml_dict, indent=4)

                try:
                    sourcetype=  Username  + "://" + helper.get_input_stanza_names()
                    event = helper.new_event(source=Username, index=index, sourcetype=sourcetype , data=json_data)
                    ew.write_event(event)
                    helper.log_info("\n\n [INFO] Event Inserted in JSON format. \n source="+Username+", index="+index+", sourcetype="+sourcetype+" , data="+json_data+" [Username : "+Username+"] \n\n")
                except:
                    helper.log_error("\n\n [ERROR] Error inserting JSON event. [Username : "+Username+"] \n\n")
                
            except:
                try:
                    sourcetype=  Username  + "://" + helper.get_input_stanza_names()
                    event = helper.new_event(source=Username, index=index, sourcetype=sourcetype , data=data)
                    ew.write_event(event)
                    helper.log_info("\n\n [INFO] Event Inserted in XML format. \n source="+Username+", index="+index+", sourcetype="+sourcetype+" , data="+data+" [Username : "+Username+"] \n\n")
                except:
                    helper.log_error("\n\n [ERROR] Error inserting XML event. [Username : "+Username+"] \n\n")

        else:
            helper.log_info(f"\n\n [INFO] Will try in 60 seconds. [Username : "+Username+"] \n\n")

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
                self.log_error("\n\n Get exception when loading global checkbox parameter names. " + str(e)+" \n\n")
                self.global_checkbox_fields = []
        return self.global_checkbox_fields


if __name__ == '__main__':
    exit_code = ModInputS2_INPUT().run(sys.argv)
    sys.exit(exit_code)


