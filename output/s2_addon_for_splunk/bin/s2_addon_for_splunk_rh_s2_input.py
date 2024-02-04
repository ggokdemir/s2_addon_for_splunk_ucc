
import import_declare_test

from splunktaucclib.rest_handler.endpoint import (
    field,
    validator,
    RestModel,
    DataInputModel,
)
from splunktaucclib.rest_handler import admin_external, util
from splunktaucclib.rest_handler.admin_external import AdminExternalHandler
import logging

util.remove_http_proxy_env_vars()


fields = [
    field.RestField(
        'index',
        required=True,
        encrypted=False,
        default='default',
        validator=validator.String(
            max_len=80, 
            min_len=1, 
        )
    ), 
    field.RestField(
        'account',
        required=True,
        encrypted=False,
        default=None,
        validator=None
    ), 
    field.RestField(
        'Server_URL',
        required=True,
        encrypted=False,
        default='http://<netbox>/appdevent/nbapi/event',
        validator=validator.String(
            max_len=15, 
            min_len=9, 
        )
    ), 
    field.RestField(
        'Username',
        required=True,
        encrypted=False,
        default='username',
        validator=validator.String(
            max_len=25, 
            min_len=4, 
        )
    ), 
    field.RestField(
        'Password',
        required=True,
        encrypted=False,
        default='password',
        validator=validator.String(
            max_len=25, 
            min_len=4, 
        )
    ), 
    field.RestField(
        'SessionId',
        required=False,
        encrypted=False,
        default='',
        validator=validator.String(
            max_len=256, 
            min_len=8, 
        )
    ), 

    field.RestField(
        'disabled',
        required=False,
        validator=None
    )

]
model = RestModel(fields, name=None)



endpoint = DataInputModel(
    's2_input',
    model,
)


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())
    admin_external.handle(
        endpoint,
        handler=AdminExternalHandler,
    )
