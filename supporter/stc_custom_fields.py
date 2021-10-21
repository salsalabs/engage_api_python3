import csv
import requests
import json
import logging

devToken = ''

headers = {
    'authToken': devToken,
    'content-type': 'application/json'
}
payloadTypes = [
    "SUBSCRIPTION_MANAGEMENT",
    "SUBSCRIBE",
    "FUNDRAISE",
    "PETITION",
    "TARGETED_LETTER",
    "REGULATION_COMMENTS",
    "TICKETED_EVENT",
    "P2P_EVENT",
    "FACEBOOK_AD"]

def scanForms(w):
    """Scan all activity forms.  Collect their UUIDs."""

    searchURL='https://api.salsalabs.org/api/developer/ext/v1/activities'

    requestedTypes = ",".join(payloadTypes)

    rPayload =  {
        'type': requestedTypes,
        'sortField': 'name',
        'sortOrder': 'ascending',
        'offset': 0,
        'count': 20
    }
    while rPayload['count'] == 20:
        r = requests.get(searchURL, headers=headers, params=rPayload)
        if (r.status_code != 200):
            logging.fatal(f"{rPayload['type']}: HTTP status code {r.status_code}")
            logging.fatal(r.body())
            exit(1)

        dPayload = r.json()['payload']
        logging.info(f"scanForms: {dPayload['offset']} of {dPayload['total']}")
        # (scanMetadata(a['id'], w) for a in dPayload['results'])
        for a in dPayload['results']:
            scanMetadata(a['id'], w)

        rPayload['count'] = dPayload['count']
        rPayload['offset'] = rPayload['offset'] + rPayload['count']

def scanMetadata(uuid, w):
    """Retrieve meta data for the specified id.  If the custom fields
    contain the 'photo_release' custom field, then write information to
    the provided CSV writer."""

    metadataURL=f"https://api.salsalabs.org/api/developer/ext/v1/activities/{uuid}/metadata"
    # logging.info(f"scanMetadata: {metadataURL}")
    r = requests.get(metadataURL, headers=headers)
    if (r.status_code != 200):
        logging.fatal(f"{uuid}: HTTP status code {r.status_code}")
        logging.fatal(r.text)
        exit(1)

    dPayload = r.json()['payload']
    # Record is malformed if it doesn't have a type, ID or name.
    if 'type' not in dPayload or 'id' not in dPayload or 'name' not in dPayload:
        logging.warning(f"scanMedata: malformed metadta record {json.dumps(dPayload)}")
    else:
        for f in dPayload['formFields']:
            if "photo" in f['name'].lower():
                w.writerow([dPayload['id'], dPayload['type'], dPayload['name']])
                logging.info(f"scanMetadata: {dPayload['id']} {dPayload['type']}, {f['name']}")

def custom(n):
    """ Returns true if the field name is not in the person, address, contact, donation."""
    nDown = n.lower()
    return "person." not in nDown and "address." not in nDown and "contact." not in nDown and "donation." not in nDown

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    f = open('forms_with_photo_release.csv', 'w')
    w = csv.writer(f)
    w.writerow(["FormID", "Type", "FormName"])
    scanForms(w)
    f.close()
    print("Matching forms can be found in 'forms_with_photo_release.csv'.")

if __name__ == '__main__':
    main()
