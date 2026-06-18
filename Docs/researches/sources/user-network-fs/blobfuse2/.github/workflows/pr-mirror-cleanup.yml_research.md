# sources/user-network-fs/blobfuse2/.github/workflows/pr-mirror-cleanup.yml

## Purpose
This workflow deletes stale `pr-mirror/<PR#>` branches created for Azure DevOps CI runs on external pull requests.

## Important APIs, Types, and Functions
It uses `actions/github-script@v9` and GitHub REST APIs `repos.listBranches`, `pulls.get`, and `git.deleteRef`.

## Control Flow
On daily schedule or manual dispatch, the script lists all branches, filters names with the `pr-mirror/` prefix, parses the PR number, fetches the PR, and deletes the mirror branch if the PR is closed, missing, or its current head SHA differs from the branch tip.

## State and Persistence Behavior
The persistent state is Git references under `refs/heads/pr-mirror/*`. The workflow mutates only those refs.

## Dependencies and Integration Points
It complements `.github/workflows/pr-mirror.yml` and supports the Azure DevOps `blobfuse2-1es_ci` workflow for fork PR validation.

## Risks and Edge Cases
It assumes branch names after the prefix are positive integers. API failures other than 404 are skipped, which can leave stale branches. It uses no checkout and no secrets, limiting blast radius.

## Test Signals
Signals are deleted mirror branches for closed or force-pushed PRs, preserved mirror branches for open PRs with matching head SHA, and workflow logs showing deletion reasons.
