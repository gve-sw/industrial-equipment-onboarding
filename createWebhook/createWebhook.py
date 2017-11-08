import settings
import requests
import time
import json



#webhookID = settings.webhookID
webhookName = 'IndustrialOnboarding'
botToken = settings.botToken
botID = settings.botID



def findNgrok():
    header = {'content-type' : "application/json"}
    url = "http://172.29.0.30:4040/api/tunnels"
    #url = "http://127.0.0.1:4040/api/tunnels"

    while True:
        try:
            response = requests.request("GET", url, headers=header, verify=False)
            status_code = response.status_code
            if (status_code == 200):
                resp =  json.loads(response.text)
                if resp['tunnels']:
                    return resp
            else:
                response.raise_for_status()
                print("Error occured in GET -->"+(response.text))
        except requests.exceptions.HTTPError as err:
            print ("Error in connection -->"+str(err))
        except requests.exceptions.ConnectionError as err:
            pass
        time.sleep(1)


# set spark headers
def setHeaders(access_token):
    accessToken_hdr = 'Bearer ' + access_token
    spark_header = {
        'Authorization':accessToken_hdr,
        'Content-Type':'application/json; charset=utf-8',
        }
    return (spark_header)


def findWebhooks(headers):
    url = "https://api.ciscospark.com/v1/webhooks/"
    response = requests.request("GET", url, headers=headers)
    webhooks = json.loads(response.text)
    return webhooks

def createWebhook(headers, targetUrl):
    url = "https://api.ciscospark.com/v1/webhooks/"
    payloadRaw = {
    "name": "IndustrialOnboarding",
    "targetUrl": targetUrl,
    "resource": "messages",
    "event": "created",
    "filter": "mentionedPeople=" + botID
    }
    payload = json.dumps(payloadRaw)

    try:
        response = requests.request("POST", url, data=payload, headers=headers, verify=False)
        status_code = response.status_code
        if (status_code == 200):
            return True
        else:
            response.raise_for_status()
            print("Error occured in POST -->"+(response.text))
    except requests.exceptions.HTTPError as err:
        print ("Error in connection -->"+str(err))




# update webhook with updated ngrok tunnel information
def updateWebhook (headers,webhookName,webhookID,targetUrl):
    url = "https://api.ciscospark.com/v1/webhooks/" + webhookID
    payload = "{\n\t\"name\": \"" + webhookName + "\",\n\t\"targetUrl\": \"" + targetUrl + "\"\n}"
    response = requests.request("PUT", url, data=payload, headers=headers)
    return response.status_code





#Address of ngrok tunnel for Dev. Used as destination for Spark webhook notifications
ngrokRaw = findNgrok()
print (ngrokRaw)
for tun in ngrokRaw['tunnels']:
    print (tun['name'])
    if tun['name'] == 'listener (http)':
    #if tun['name'] == 'command_line (http)':    
        ngrokTunnel = tun['public_url']
        #print (ngrokTunnel)
        break
    else:
        print ('Ngrok tunnel not created')


headers = setHeaders(botToken)

webhookTest = False

existingWebhook = findWebhooks(headers)
print(existingWebhook)

if not existingWebhook['items']:
    createTest = createWebhook(headers, ngrokTunnel)
    if createTest == True:
        webhookTest = True
        print ('Webhook Created')

else:
    for hooks in existingWebhook['items']:
        if hooks['name'] == 'IndustrialOnboarding':        
            updateResult = updateWebhook(headers, webhookName, hooks['id'], ngrokTunnel)

            if updateResult == 200:
                print ('WebHook Updated')
                webhookTest = True
            else:
                print (updateResult)

if webhookTest == False:
    createHook = createWebhook(headers, ngrokTunnel)
    if createHook == True:
        print ('Webhook Created')

#b
