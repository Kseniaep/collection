import requests
import json
params ={
       'Accept': 'application/vnd.github.v3+json'
}
username = 'kseniaep'
response = requests.get(f'https://api.github.com/users/{username}/repos', params = params)
j_response = response.json()
print(f'Репозитарии пользователя {username}')
for rep in j_response:
    print(rep['name'])
with open ('response.json','w') as f:
    json.dump(j_response,f)

