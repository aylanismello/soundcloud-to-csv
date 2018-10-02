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
    'https://soundcloud.com/umdotdot': {}
}

handle_names = {
    'https://soundcloud.com/umdotdot': 'Um'
}
def add_users(user_collection):
    users = {}
    user_data = { 'emails': [], 'youtube': None }

    for user in user_collection:
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', user.description or '')
        if emails:
            # users[user.username] = emails
            user_data['emails'] = emails
            users[user.username] = user_data
        # else:
        #     emails = []
        #     web_profiles = client.get(f'/users/{user.id}/web-profiles')
        #     for web_profile in web_profiles:
        #         if web_profile.service == 'email':
        #             emails.append(web_profile.url)
        #     if len(emails):
        #         user_data['emails']= emails
        #         users[user.username] = user_data
                # users[user.username] = emails
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
    fieldnames = ['root_handle', 'handle', 'emails']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for url, users in handle_urls.items():
        for handle, user_data in users.items():
            writer.writerow({'root_handle': handle_names[url], 'handle': handle, 'emails': ', '.join(user_data['emails'])})
