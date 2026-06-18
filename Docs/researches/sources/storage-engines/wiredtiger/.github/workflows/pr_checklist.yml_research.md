# sources/storage-engines/wiredtiger/.github/workflows/pr_checklist.yml

## Purpose
This GitHub Actions workflow posts a structured review checklist comment when a pull request is opened. It is process automation rather than build/test execution.

## Important APIs, Types, and Functions
The workflow triggers on `pull_request` type `opened`, runs one `ubuntu-latest` job, and uses `actions/github-script@v7` to call `github.rest.issues.createComment`.

## Control Flow, State, and Dependencies
On PR open, the script builds a Markdown comment with review readiness, safety, compatibility, test coverage, risk, and change-type questions, then posts it to the PR issue thread. State is stored as a GitHub comment.

## Integration Points, Risks, and Test Signals
It integrates with GitHub Issues/PR comments and links repository risk/testing docs. Risks include duplicate comments on reopen only if workflow trigger changes, and reliance on `GITHUB_TOKEN` permissions. Signal is the comment appearing on new PRs.
