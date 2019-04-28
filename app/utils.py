import json
import requests

def make_tf_serving_request(data,url):
    data = json.dumps({"signature_name": "serving_default", "instances": data})
    print('Data: {}'.format(data))
    headers = {"content-type": "application/json"}
    json_response = requests.post(url+':predict', data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    return predictions

if __name__ == '__main__':
    """
    Does nothing
    """