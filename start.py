import soundcloud
import sys
import pdb
import re
import csv

client = soundcloud.Client(client_id='caf73ef1e709f839664ab82bef40fa96')


try:
    file_name = sys.argv[1]
except:
    raise Exception('Please provide file name')


handle_urls = {
    'https://soundcloud.com/burncartel': {},
    'https://soundcloud.com/hoodedyouth': {}
}

handle_names = {
    'https://soundcloud.com/burncartel': 'Burn Cartel',
    'https://soundcloud.com/hoodedyouth': 'Hooded Youth'
}
def add_users(user_collection):
    users = {}

    for user in user_collection:
        user_data = { 'emails': [], 'youtube': '' }
        # find emails in description
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', user.description or '')
        if emails:
            user_data['emails'] = emails

        # yank webprofiles one by one
        web_profiles = client.get(f'/users/{user.id}/web-profiles')
        for web_profile in web_profiles:
            if web_profile.service == 'email':
                user_data['emails'].append(web_profile.url)
            if web_profile.service == 'youtube' and not user_data['youtube']:
                # pdb.set_trace()
                user_data['youtube'] = (web_profile.url)


        users[user.username] = user_data

    return users

for url, users in handle_urls.items():
    user_id = client.get('/resolve', url=url).id
    followings = client.get(f'/users/{user_id}/followings', limit=200)
    users = {**users, **add_users(followings.collection)}

    next_href = followings.next_href
    while next_href:
        followings = client.get(next_href)
        users = {**users, **add_users(followings.collection)}
        next_href = followings.next_href
    handle_urls[url] = users


with open(f'./data/{file_name}.csv', mode='w') as csv_file:
    fieldnames = ['root_handle', 'handle', 'emails', 'youtube']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for url, users in handle_urls.items():
        for handle, user_data in users.items():
            writer.writerow({'root_handle': handle_names[url], 'handle': handle, 'emails': ', '.join(user_data['emails']), 'youtube': user_data['youtube'] })
