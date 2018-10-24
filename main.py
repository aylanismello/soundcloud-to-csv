import soundcloud
import sys
import json
import pdb
import re
import csv

client = soundcloud.Client(client_id='caf73ef1e709f839664ab82bef40fa96')


try:
    file_name = sys.argv[1]
except:
    raise Exception('Please provide file name')

with open('./handles.json') as f:
    handles = json.load(f)['handles']


handle_urls = {}
handle_names = {}

for url, handle_name in handles.items():
    handle_urls[url] = {}
    handle_names[url] = handle_name

pdb.set_trace()


def add_users(user_collection):
    users = {}

    for user in user_collection:

        user_data = {
            'emails': [],
            'youtube': '',
            'instagram': '',
            'facebook': '',
            'twitter': '',
            'city': user.city,
            'country': user.country,
            'followers_count': user.followers_count
        }
        # find emails in description
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', user.description or '')
        if emails:
            user_data['emails'] = emails

        # yank webprofiles one by one
        web_profiles = client.get(f'/users/{user.id}/web-profiles')
        print(f'fetching web profile for {user.username}')
        for web_profile in web_profiles:
            if web_profile.service == 'email':
                user_data['emails'].append(web_profile.url)
            if web_profile.service == 'youtube' and not user_data['youtube']:
                user_data['youtube'] = (web_profile.url)
            if web_profile.service == 'twitter' and not user_data['twitter']:
                user_data['twitter'] = (web_profile.url)
            if web_profile.service == 'instagram' and not user_data['instagram']:
                user_data['instagram'] = (web_profile.url)
            if web_profile.service == 'facebook' and not user_data['facebook']:
                user_data['facebook'] = (web_profile.url)


        users[user.username] = user_data

    return users

count = 0

for url, users in handle_urls.items():
    count += 1
    print(f'on user {count}')
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
