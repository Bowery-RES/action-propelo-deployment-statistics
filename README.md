# action-propelo-deployment-statistics
Action to send service deployment/release statistics

# Required parameters
- **github_repository** - Github Repository: **$GITHUB_REPOSITORY** internal github environment variable (for example: _octocat/Hello-World_)
- **commit_sha** - The commit SHA that triggered the workflow: **$GITHUB_SHA**
- **environment** - Application/service environment: _dev, staging, production_
- **github_user** - Github user login for github API requests
- **github_token** - Github token of **github_user**
- **propelo_token** - Propelo Token for API requests
- **propelo_deployment_instance_guid** - Propelo **jenkins_instance_guid** predefined variable

# IMPORTANT
The Action must be used after the Github Release publishing and from the **commit** with the **release tag**!

# Usage
```
jobs:
  propelo:
    runs-on: ubuntu-latest
    name: Submit deployment statistic to propelo
    steps:
      - uses: actions/action-propelo-deployment-statistics@v1
        with:
          github_repository: ${{ env.GITHUB_REPOSITORY }}
          commit_sha: ${{ env.GITHUB_SHA }}
          environment: 'production' # Or some internal env variable
          github_user: ${{ secrets.GITHUB_USER }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          propelo_token: ${{ secrets.PROPELO_TOKEN }}
          propelo_deployment_instance_guid: ${{ secrets.PROPELO_GUID}}
```