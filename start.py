import soundcloud
import pdb
import re
import csv

client = soundcloud.Client(client_id='caf73ef1e709f839664ab82bef40fa96')

handle_urls = {
    'https://soundcloud.com/user-733227616': {},
    'https://soundcloud.com/k_sadilla': {},
    'https://soundcloud.com/thunderstone-radio': {},
    'https://soundcloud.com/user-658289159': {},
    'https://soundcloud.com/user-441287236': {},
    'https://soundcloud.com/my-big-dill': {}
}

handle_names = {
    'https://soundcloud.com/user-733227616': 'Drty Fxn Svge',
    'https://soundcloud.com/k_sadilla': 'K Sadilla',
    'https://soundcloud.com/thunderstone-radio': 'Thunderstone Radio ',
    'https://soundcloud.com/user-658289159': 'Dre big rxx',
    'https://soundcloud.com/user-441287236': 'Last time you rolled',
    'https://soundcloud.com/my-big-dill': 'Molly mcthizzletoes'
}

# receives user collection (LIST)
#  { 'swinga': ['first', 'second']}
def add_users(user_collection):
    users = {}

    for user in user_collection:
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', user.description or '')
        if emails:
            users[user.username] = emails
        else:
            emails = []
            web_profiles = client.get(f'/users/{user.id}/web-profiles')
            for web_profile in web_profiles:
                if web_profile.service == 'email':
                    emails.append(web_profile.url)
            if len(emails):
                users[user.username] = emails
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


with open('thunderstone_emails.csv', mode='w') as csv_file:
    fieldnames = ['root_handle', 'handle', 'emails']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for url, users in handle_urls.items():
        for handle, emails in users.items():
            writer.writerow({'root_handle': handle_names[url], 'handle': handle, 'emails': ', '.join(emails)})
