# action-propelo-deployment-statistics
Action to submit application/service Release statistics

# Required parameters
- **github_repository** - Github Repository: **$GITHUB_REPOSITORY** internal github environment variable (for example: _octocat/Hello-World_)
- **commit_sha** - The Release commit SHA that triggered the Release workflow: **$GITHUB_SHA**
- **release_tag** - The Release TAG that triggered the workflow. A part of the environment variable: **${GITHUB_REF/refs\/tags\//}**
- **environment** - Application/service environment: _dev, staging, production_
- **github_user** - Github user login for github API requests
- **github_token** - Github token of **github_user**
- **propelo_token** - Propelo Token for API requests
- **propelo_deployment_instance_guid** - Propelo **jenkins_instance_guid** predefined variable

# IMPORTANT
Action should be used after Github Release. Please use separate Github Actions in your repository -> the event **'release'** with type/payload **'released'**

# Usage
```
on:
  release:
    types: [released]

jobs:
  propelo:
    runs-on: ubuntu-latest
    name: Submit deployment statistic to propelo
    steps:
      - name: Prepare common parameters
        id: env-vars
        run: |
          echo "::set-output name=github_repository::${GITHUB_REPOSITORY}"
          echo "::set-output name=commit_sha::${GITHUB_SHA}"
          echo "::set-output name=release_tag::${GITHUB_REF/refs\/tags\//}"
      
      - uses: Bowery-RES/action-propelo-deployment-statistics@v2
        with:
          github_repository: ${{ steps.env-vars.outputs.github_repository }}
          commit_sha: ${{ steps.env-vars.outputs.commit_sha }}
          release_tag: ${{ steps.env-vars.outputs.release_tag }}
          environment: 'production'
          github_user: ${{ secrets.GH_USER }}
          github_token: ${{ secrets.GH_TOKEN }}
          propelo_token: ${{ secrets.PROPELO_TOKEN }}
          propelo_deployment_instance_guid: ${{ secrets.PROPELO_GUID}}
```