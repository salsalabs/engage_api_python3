import json
import requests

devToken=''
intToken=''
host='https://api.salsalabs.org'

def getActivities():
    """Return activities to match the activityIds in file `activity_ids.txt`.
    ActivityIds are in this file courtesy of `search_p2p_fundraisers.batch`,
    grep and set."""

    s = requests.Session()
    s.headers.update({
        "Content-Type": "application/json",
        "authToken": intToken})

    # Retrieve the list of activityIds.
    with open("activity_ids.txt", "r") as f:
        activityIds = f.readlines()
        f.close()
    activityIds = [id.rstrip() for id in activityIds]

    # Return activity records for each of these activitIds.
    payload = {
        "payload": {
            "offset": 0,
            "count": 20,
            "activityIds": activityIds
        }
    }
    cmd = '/api/integration/ext/v1/activities/search'
    url = f"{host}{cmd}"
    # Needs to be a string before it's submitted.
    p = json.dumps(payload)
    resp = s.post(url, data=p)
    resp.raise_for_status()
    return resp.json()['payload']['activities']

def main():
    activities = getActivities()
    print(activities)

if __name__ == '__main__':
    main()
