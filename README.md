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