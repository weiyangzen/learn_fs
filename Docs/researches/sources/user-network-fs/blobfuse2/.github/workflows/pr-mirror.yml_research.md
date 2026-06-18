# sources/user-network-fs/blobfuse2/.github/workflows/pr-mirror.yml

## Purpose
This workflow lets a maintainer mirror a pull request head commit into an upstream `pr-mirror/<PR#>` branch so Azure DevOps CI can be manually queued for fork PR code without running fork-authored workflow code in GitHub Actions.

## Important APIs, Types, and Functions
It uses `actions/github-script@v9` for reaction/comment/status APIs, `actions/checkout@v6`, `git fetch` from `refs/pull/<n>/head`, and `git push --force-with-lease` to the mirror ref.

## Control Flow
The job only runs when an issue comment is exactly `/mirror`, the issue is a pull request, and the commenter is OWNER or MEMBER. It reacts to the comment, resolves PR head SHA/number/state, refuses closed PRs, checks out the upstream repo without fork code, fetches `pull/<number>/head`, verifies fetched SHA equals the PR head SHA, refreshes existing mirror tracking ref if present, force-pushes the SHA to `pr-mirror/<number>`, comments with maintainer instructions, and sets a pending commit status named `pr-mirror`.

## State and Persistence Behavior
Persistent state includes mirror branches, PR comments, comment reactions, and commit status records. The workflow does not persist artifacts.

## Dependencies and Integration Points
It integrates GitHub PR review workflow with Azure DevOps `blobfuse2-1es_ci`. Comments explicitly instruct maintainers to run the ADO pipeline against the mirror branch.

## Risks and Edge Cases
Security depends on ADO loading trusted pipeline YAML from a fixed ref, as documented in comments. The exact-body trigger ignores whitespace or additional text. `--force-with-lease` reduces accidental overwrite risk but still updates branch state.

## Test Signals
Signals include a maintainer `/mirror` comment creating or updating the expected branch, SHA verification logs, a PR comment containing the branch link, and pending commit status on the mirrored SHA.
