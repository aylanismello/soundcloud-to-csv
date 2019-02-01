import soundcloud
import sys
import json
import pdb
import re
import csv
from pathlib import Path

NEWEST_EPISODE = 81
DAT_PATH = './bc_episode_ids.dat'

client = soundcloud.Client(client_id='caf73ef1e709f839664ab82bef40fa96')

try:
    file_name = sys.argv[1]
except:
    raise Exception('Please provide file name')

scrape_type = 0
while scrape_type not in range(1,4):
    try:
        scrape_type = int(input('1. Get all followers\n2. Get all followings\n3. Get all based on playlists\n'))
    except:
        raise Exception('Must provide a number as an option')
        
if scrape_type == 1:
    scrape_type = 'followers'
elif scrape_type == 2:
    scrape_type = 'followings'
else:
    scrape_type = 'bc_episodes'


with open('./handles.json') as f:
    handles = json.load(f)['handles']


handle_urls = {}
handle_names = {}

for url, handle_name in handles.items():
    handle_urls[url] = {}
    handle_names[url] = handle_name


def add_handles_to_users(user_collection):
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
            'followers_count': user.followers_count,
            'permalink_url': user.permalink_url
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


def set_follow_x_users(users):
    user_id = client.get('/resolve', url=url).id
    selected_sc_users = client.get(f'/users/{user_id}/{scrape_type}', limit=200)
    users = {**users, **add_handles_to_users(selected_sc_users.collection)}

    next_href = selected_sc_users.next_href
    while next_href:
        selected_sc_users = client.get(next_href)
        users = {**users, **add_handles_to_users(selected_sc_users.collection)}
        next_href = selected_sc_users.next_href
    return users

def set_featured_bc_users():
    selected_sc_users = []

    dat_file = Path(DAT_PATH)
    if not dat_file.is_file():
        with open(DAT_PATH, mode='w+') as f:            
            for episode_num in range(NEWEST_EPISODE + 1):
                try:
                    playlist = client.get('/resolve', url=f'https://soundcloud.com/hoodedyouth/sets/burn-cartel-radio-episode-{episode_num}')
                except Exception as e:
                    # print(str(e))
                    print(f'fucked up on episode {episode_num} but ok')
                    continue
                for track in playlist.tracks:
                    user_id = track['user']['id']
                    f.write(f'{str(user_id)},')
    else:
        with open(DAT_PATH, mode='r') as f:
            user_ids = f.read().split(',')[0:-1]            
            for user_id in user_ids:
                selected_sc_users.append(client.get(f'/users/{user_id}'))

    return { **add_handles_to_users(selected_sc_users) }
    
count = 0    

for url, users in handle_urls.items():
    count += 1
    print(f'on user {count}')

    if 'follow' in scrape_type:
        handle_urls[url] = set_follow_x_users(users)
    else:
        handle_urls[url] = set_featured_bc_users()

with open(f'./data/{file_name}-{scrape_type}.csv', mode='w') as csv_file:
    fieldnames = ['root_handle', 'handle', 'permalink_url', 'youtube', 'city', 'country', 'followers_count', 'emails', 'instagram', 'facebook', 'twitter']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for url, users in handle_urls.items():
        for handle, user_data in users.items():
            writer.writerow({'root_handle': handle_names[url], 'handle': handle, 'permalink_url': user_data['permalink_url'], 'emails': ', '.join(user_data['emails']), 
            'youtube': user_data['youtube'], 'twitter': user_data['twitter'], 'instagram': user_data['instagram'], 'facebook': user_data['facebook'], 
            'city': user_data['city'], 'country': user_data['country'], 'followers_count': user_data['followers_count']
             })
