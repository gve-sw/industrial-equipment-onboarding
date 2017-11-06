import settings
import requests
import json



webhookID = settings.webhookID
webhookName = settings.webhookName
botToken = settings.botToken



def findNgrok():
    header = {'content-type' : "application/json"}
    url = "http://172.30.0.30:4040/api/tunnels"
    try:
        response = requests.request("GET", url, headers=header, verify=False)
        status_code = response.status_code
        if (status_code == 200):
            return json.loads(response.text)
        else:
            response.raise_for_status()
            print("Error occured in GET -->"+(response.text))
    except requests.exceptions.HTTPError as err:
        print ("Error in connection -->"+str(err))
    finally:
        if response : response.close()


#Address of ngrok tunnel for Dev. Used as destination for Spark webhook notifications
ngrokRaw = findNgrok()
#print (ngrokRaw)
for tun in ngrokRaw['tunnels']:
    #print (tun['name'])
    if tun['name'] == 'listener (http)':
        ngrokTunnel = tun['public_url']
        #print (ngrokTunnel)
        break
    else:
        print ('Ngrok tunnel not created')


# set spark headers
def set_headers(access_token):
    accessToken_hdr = 'Bearer ' + access_token
    spark_header = {
        'Authorization':accessToken_hdr,
        'Content-Type':'application/json; charset=utf-8',
        }
    return (spark_header)

# update webhook with updated ngrok tunnel information
def update_webhook (the_headers,webhookName,webhookID,targetUrl):
    url = "https://api.ciscospark.com/v1/webhooks/" + webhookID
    payload = "{\n\t\"name\": \"" + webhookName + "\",\n\t\"targetUrl\": \"" + targetUrl + "\"\n}"
    response = requests.request("PUT", url, data=payload, headers=the_headers)
    return response.status_code


headers = set_headers(botToken)
updateResult = update_webhook(headers, webhookName, webhookID, ngrokTunnel)

if updateResult == '200':
    print ('WebHook Updated')
else:
    print (updateResult)

#b
