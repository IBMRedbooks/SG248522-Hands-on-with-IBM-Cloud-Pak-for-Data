#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys
import requests, json
import ast

def getToken(cpd_url,cpd_username,cpd_password):
    url = cpd_url + '/v1/preauth/validateAuth'
    #print("get token url: ", url)
    response = requests.get(url,auth=(cpd_username,cpd_password),verify=False)
    #print("response: ", response)
    wml_token = response.json()["accessToken"]
    #print("token: ", wml_token)
    return wml_token

def predictChurn(wml_token,scoring_url,flds,vals):
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + wml_token}
    
    payload_scoring = {"input_data": [{"fields": flds, "values": vals}]}
    response_scoring = requests.post(scoring_url, json=payload_scoring, headers=header, verify=False)
    churn = json.loads(response_scoring.text)
    return churn
    
def getProb(prediction):
    pred = prediction['predictions'][0]['values'][0][-1]
    if pred == 'T':
        prob = prediction['predictions'][0]['values'][0][-3][1]
    else:
        prob = prediction['predictions'][0]['values'][0][-3][0]
    return prob
    
def main(dict):
    cpd_url = dict['cpd_url']
    cpd_username = dict['cpd_username']
    cpd_password = dict['cpd_password']
    try:
        scoring_url = dict['scoring_url']
        flds_array = ast.literal_eval(dict['fields'])
        vals_array = ast.literal_eval(dict['values'])
    except:
        print("error")
        response = {"error": "not all required parameters are provided. Please make sure you pass the scoring_url, fields, and values parameters"}
        return response

    wml_token = getToken(cpd_url,cpd_username,cpd_password)
    churn_prediction = predictChurn(wml_token,scoring_url,flds_array,vals_array)
    ##print("churn prediction: ", churn_prediction)
    predlabel = churn_prediction['predictions'][0]['values'][0][-1]
    print("predlabel: ", predlabel)
    predprob = getProb(churn_prediction)
    print("predprob: ", predprob)
    response = {"label": predlabel, "prob":predprob}
    return response