import json
import requests
import uuid
import logging

class LbryRpcException(Exception):
    pass

class LbryRpcClient:
    def __init__(self, endpoint):
        self.__endpoint = endpoint
    def __call(self, method, params):
        headers = {"content-type": "application/json"}
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4())
        }
        logging.debug("Making request: {}".format(payload))

        try:
            response = requests.post(self.__endpoint, data=json.dumps(payload),
                                     headers=headers).json()
        except json.decoder.JSONDecodeError:
            raise LbryRpcException("Could not decode JSON response: {e}".format(e=response))
        if 'error' in response:
            raise LbryRpcException("Error in json-rpc response: {e}".format(
                e=response['error']))
        if 'jsonrpc' not in response or 'result' not in response:
            raise LbryRpcException("Error in response: {e}".format(e=response))
        ## LBRY app has a broken JSON-RPC implementation and does not return an id:
        ### assert response["id"] == payload["id"]
        return response["result"]

    def __getattr__(self, attr):
        return lambda params: self.__call(attr, params)
