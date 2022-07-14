from datetime import datetime
from tabulate import tabulate
import json
import os
import sys
import requests

def api_request(API_URL, requestDescription, githubUser, githubToken, timeout=10):
    githubAPIResponse = {}
    try:
        githubAPIGetResponse = requests.get(API_URL, auth=(githubUser, githubToken), timeout=timeout)
        githubAPIGetResponse.raise_for_status()
    except requests.exceptions.HTTPError as httpError:
        print(f"Github API request '{requestDescription}' -> Http Error:", httpError)
        sys.exit(0)
    except requests.exceptions.ConnectionError as connectionError:
        print(f"Github API request '{requestDescription}' -> Error Connecting:", connectionError)
        sys.exit(0)
    except requests.exceptions.Timeout as timeoutError:
        print(f"Github API request '{requestDescription}' -> Timeout Error:", timeoutError)
        sys.exit(0)
    except requests.exceptions.RequestException as requestExceptionError:
        print(f"Github API request '{requestDescription}' -> Oops: Something Else", requestExceptionError)
        sys.exit(0)
    githubAPIResponse['content'] = githubAPIGetResponse.content
    githubAPIResponse['links']   = githubAPIGetResponse.links
    return githubAPIResponse

# Initiolize list for print tables
data = []

# Check Environment variables
data.append(["Variable name", "Value"])
try:
    commitSHA = os.environ['COMMIT_SHA']
    data.append(["COMMIT_SHA", commitSHA])
except KeyError:
    print("Please define the environment variable 'COMMIT_SHA'")
    sys.exit(0)

try:
    appEnv = os.environ['ENVIRONMENT']
    data.append(["ENVIRONMENT", appEnv])
    if appEnv != 'production':
        print(f"This is not a PRODUCTION environment...\n'ENVIRONMENT' == {appEnv} !")
        sys.exit(0)
except KeyError:
    print("Please define the environment variable 'ENVIRONMENT'")
    sys.exit(0)

try:
    githubRepo = os.environ['GITHUB_REPOSITORY']
    data.append(["GITHUB_REPOSITORY", githubRepo])
except KeyError:
    print("Please define the environment variable 'GITHUB_REPOSITORY'")
    sys.exit(0)

try:
    githubUser = os.environ['GITHUB_USER']
    data.append(["GITHUB_USER", githubUser])
except KeyError:
    print("Please define the environment variable 'GITHUB_USER'")
    sys.exit(0)

try:
    githubToken = os.environ['GITHUB_TOKEN']
    data.append(["GITHUB_TOKEN", "*****"])
except KeyError:
    print("Please define the environment variable 'GITHUB_TOKEN'")
    sys.exit(0)

try:
    propeloToken = os.environ['PROPELO_TOKEN']
    data.append(["PROPELO_TOKEN", "*****"])
except KeyError:
    print("Please define the environment variable 'PROPELO_TOKEN'")
    sys.exit(0)

try:
    propeloGUID = os.environ['PROPELO_GUID']
    data.append(["PROPELO_GUID", "*****"])
except KeyError:
    print("Please define the environment variable 'PROPELO_GUID'")
    sys.exit(0)
print(tabulate(data, headers='firstrow', tablefmt='fancy_grid'))
data.clear()

# Get Application/service name
appName = githubRepo.split('/')

# Set APIs URL
githubAPIGetCommitRequest = 'https://api.github.com/repos/' + githubRepo
propeloPostURL = 'https://api.levelops.io/v1/generic-requests'

# Get latest Releases
tagsNames = []
githubJSON = api_request(githubAPIGetCommitRequest + '/releases?per_page=10', f'GET latest Release', githubUser, githubToken, timeout=10)
try:
    dataJSON = json.loads(githubJSON['content'])
    data.append(["Release", "Date", "ID", "Tag Name", "Prerelease", "Draft", "Target branch"])
    for i in dataJSON:
        if i['prerelease']== False and i['draft']== False:
            tagsNames.append(i['tag_name'])
            if len(tagsNames) == 1:
                print(f'\nLatest released Release TAG:\t{i["tag_name"]}')
                releaseName = i['tag_name']
                print(f'Latest released Release ID:\t{i["id"]}')
                releaseID = i['id']
                print(f'Latest released Release Author:\t{i["author"]["login"]}')
                releaseAuthor = i['author']['login']
                print(f'Latest released Release Time:\t{i["published_at"]}')
                releaseTime = i['published_at']
                releaseURL = i['html_url']
        data.append([i['name'], i['published_at'], i['id'], i['tag_name'], i['prerelease'], i['draft'], i['target_commitish']])
    print(tabulate(data, headers='firstrow', tablefmt='fancy_grid'))
except json.decoder.JSONDecodeError:
    print("Response [githubAPIGetLastCommitResponse] could not be converted to JSON")
    sys.exit(0)

data.clear()

if len(tagsNames) < 2:
    print("Looks like this is the FIRST release.")
    sys.exit(0)

# Get 20 latest tags
tags = {}
githubJSON = api_request(githubAPIGetCommitRequest + '/tags?per_page=20', 'Get 20 latest tags', githubUser, githubToken, timeout=10)
try:
    tagsJSON = json.loads(githubJSON['content'])
    for i in tagsJSON:
        if i['name'] in tagsNames[:2]:
            tags[i['name']] = i["commit"]["sha"]
    print(f'\nTwo latest tags & commits SHA:\t{tags}')
    if releaseName != tagsNames[0] or tags[releaseName] != commitSHA:
        print(f"Current release '{releaseName}' is not included in tags: '{tagsNames}' or current deployment commit not tagget by release tag {tags}")
        sys.exit(0)
except json.decoder.JSONDecodeError:
    print("Response (latest releases tags) could not be converted to JSON")
    sys.exit(0)

githubAPIGetResponse = api_request(githubAPIGetCommitRequest + '/compare/' + tagsNames[1] + '...' + tagsNames[0] + '?per_page=100', 'GET releases diffs', githubUser, githubToken, timeout=10)
nextPage = githubAPIGetResponse['links']['first']
diffCommits = []
while True:
    githubAPIGetResponse = api_request(nextPage['url'], 'GET releases diffs next page', githubUser, githubToken, timeout=10)
    githubJSON = githubAPIGetResponse['content']
    try:
        releasesDiffsJSON = json.loads(githubJSON)
        for i in releasesDiffsJSON["commits"]:
            diffCommits.append(i["sha"])
            data.append([i["sha"], i["commit"]["committer"]["name"], i["commit"]["committer"]["date"]]) #, i["sha"], i["commit"]["message"], i["commit"]["committer"]["date"]
    except json.decoder.JSONDecodeError:
        print("Response (releases diff commits) could not be converted to JSON")
        sys.exit(0)
    if 'next' not in githubAPIGetResponse['links']:
        break
    nextPage = githubAPIGetResponse['links']['next']

# Prepare payload JSON
propeloJSON = {}
propeloJSON["name"]       = f'{releaseName}'
propeloJSON["sha"]        = commitSHA
propeloJSON["fullName"]   = f'{releaseName}'
propeloJSON["user"]       = releaseAuthor
propeloJSON["date"]       = releaseTime
propeloJSON["number"]     = releaseID
propeloJSON["url"]        = releaseURL
print(f'\nParalelo parameters:\ncommit_sha:\t{propeloJSON["sha"]}\nName:\t{propeloJSON["name"]}\nDate:\t{propeloJSON["date"]}\nUser:\t{propeloJSON["user"]}\nURL:\t{propeloJSON["url"]}\nNumber:\t{propeloJSON["number"]}')
print(f'\nRelease commits count:\t{len(diffCommits)}')
print(tabulate(data, tablefmt='fancy_grid'))

try:
    propeloReleaseDate = propeloJSON["date"]
except KeyError:
    print(f"Looks like 'propeloJSON' is empty ... or it's not a 'master' branch or !Release PR")
    sys.exit(0)

# Change date type/format
if propeloReleaseDate.find('Z') > 0:
    propeloReleaseDate = propeloReleaseDate.rstrip('Z')

propeloJSON["date"] = format(datetime.timestamp(datetime.fromisoformat(propeloReleaseDate))*1000, '.0f')
propeloJSON["duration"] = format((datetime.timestamp(datetime.now()) - datetime.timestamp(datetime.fromisoformat(propeloReleaseDate)))*1000, '.0f')
print(f"\nPrepared JSON's data:\n--->\n{propeloJSON}\n<---")

toPropeloPayload = {}
toPropeloPayload["job_name"]                 = appName[1] + '-release' #appName[1] + '-release'; propeloJSON["name"]
toPropeloPayload["user_id"]                  = propeloJSON["user"]
toPropeloPayload["job_run_params"]           = [
    {"type": "StringParameterValue",  "name": "PRODUCT_NAME",           "value": f'{appName[1]}'},
    {"type": "StringParameterValue",  "name": "PRODUCT_BRANCH",         "value": f'{propeloJSON["name"]}'},
    {"type": "StringParameterValue",  "name": "BUILD_TYPE",             "value": "Deployment"},
    {"type": "StringParameterValue",  "name": "RELEASE_COMMIT_SHA",     "value": f'{propeloJSON["sha"]}'},
    {"type": "StringParameterValue",  "name": "RELEASE_COMMIT_URL",     "value": f'{propeloJSON["url"]}'},
    {"type": "StringParameterValue",  "name": "RELEASE_COMMITS",        "value": f'{len(diffCommits)}'},
    {"type": "StringParameterValue",  "name": "Environment",            "value": f'{appEnv}'},
    {"type": "BooleanParameterValue", "name": "SONARQUBE",              "value": "true"},
]
toPropeloPayload["repo_url"]                 = None
toPropeloPayload["scm_user_id"]              = None
toPropeloPayload["start_time"]               = propeloJSON["date"]
toPropeloPayload["result"]                   = "SUCCESS"
toPropeloPayload["duration"]                 = propeloJSON["duration"]
toPropeloPayload["build_number"]             = propeloJSON["number"]
toPropeloPayload["jenkins_instance_guid"]    = propeloGUID
toPropeloPayload["jenkins_instance_name"]    = "Github Actions"
toPropeloPayload["jenkins_instance_url"]     = propeloJSON["url"]
toPropeloPayload["job_run"]                  = None
toPropeloPayload["job_full_name"]            = propeloJSON["fullName"]
toPropeloPayload["job_normalized_full_name"] = propeloJSON["fullName"]
toPropeloPayload["branch_name"]              = None
toPropeloPayload["module_name"]              = None
toPropeloPayload["scm_commit_ids"]           = diffCommits
toPropeloPayload["trigger_chain"]            = [
    {"id": "SCMTrigger", "type": "SCMTriggerCause"}
]

toPropeloJSON = {}
toPropeloJSON["request_type"] = "JenkinsPluginJobRunComplete"
try:
    toPropeloJSON["payload"] = json.dumps(toPropeloPayload)
    toPropeloData            = json.dumps(toPropeloJSON)
except json.decoder.JSONDecodeError:
    print("Propelo payload could not be converted to JSON")
    sys.exit(0)


print(f'\nPOST statistics to Propelo ...') # {json.dumps(toPropeloJSON)}
propeloRequestHeaders = {'Authorization' : f'Apikey {propeloToken}', 'Content-Type': 'application/json'}
try:
    propeloAPIResponse = requests.post(propeloPostURL, data=toPropeloData, headers=propeloRequestHeaders, timeout=10)
    propeloAPIResponse.raise_for_status()
except requests.exceptions.HTTPError as httpError:
    print("Http Error:", httpError)
    sys.exit(0)
except requests.exceptions.ConnectionError as connectionError:
    print("Error Connecting:", connectionError)
    sys.exit(0)
except requests.exceptions.Timeout as timeoutError:
    print("Timeout Error:", timeoutError)
    sys.exit(0)
except requests.exceptions.RequestException as requestExceptionError:
    print("Oops: Something Else", requestExceptionError)
    sys.exit(0)
print(f'Done!')