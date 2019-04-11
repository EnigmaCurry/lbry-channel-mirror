import json
import requests
import uuid
import logging
import pprint

class LbryRpcException(Exception):
    pass

class LbryRpcClient:
    def __init__(self, endpoint):
        self.__endpoint = endpoint
        self.__pprint = pprint.PrettyPrinter(indent=2)

    def __call(self, method, params):
        headers = {"content-type": "application/json"}
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4())
        }
        logging.debug("Making request: {}".format(self.__pprint.pformat(payload)))

        try:
            response = requests.post(self.__endpoint, data=json.dumps(payload),
                                     headers=headers).json()
        except json.decoder.JSONDecodeError:
            raise LbryRpcException("Could not decode JSON response: {e}".format(e=response))
        if "error" in response:
            raise LbryRpcException("Error in json-rpc response: {e}".format(
                e=response["error"]))
        if "jsonrpc" not in response or "result" not in response:
            raise LbryRpcException("Error in response: {e}".format(e=response))
        ## LBRY app has a broken JSON-RPC implementation and does not return an id:
        ### assert response["id"] == payload["id"]
        logging.debug("Response: {}".format(self.__pprint.pformat(response)))
        return response

    def __paginate(self, method, params, max_pages=None):
        current_page = page1 = self.__call(method, params)['result']

        if "total_pages" in page1:
            if max_pages is not None and max_pages < page1["total_pages"]:
                pages_to_get = max_pages
            else:
                pages_to_get = page1["total_pages"]

            while current_page["page"] < pages_to_get:
                yield current_page
                current_page = self.__call(method, dict(params, page=current_page["page"]+1))['result']
            else:
                yield current_page
        else:
            yield current_page

    def __getattr__(self, attr):
        def wrapper(params, max_pages=None):
            yield from self.__paginate(attr, params, max_pages)
        return wrapper
