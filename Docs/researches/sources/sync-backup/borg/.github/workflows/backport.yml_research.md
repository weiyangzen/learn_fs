# sources/sync-backup/borg/.github/workflows/backport.yml Research

## Purpose

`backport.yml` automates creation of backport pull requests after a PR is merged or when a maintainer comments `/backport` on a pull request. It uses labels matching `port/<target>` to select backport destinations.

## Important APIs, Types, and Functions

The workflow is triggered by `pull_request_target` on closed PRs and `issue_comment` on created comments. Permissions grant `contents: write` and `pull-requests: write`. The single job runs on `ubuntu-24.04`, times out after five minutes, checks out the repository with `actions/checkout@v6`, and invokes `korthout/backport-action@v4` with `label_pattern: '^port/(.+)$'`.

## Control Flow

The job-level `if` permits execution only for merged pull requests or issue comments on PRs where the commenter is not the known backport-action bot and the comment starts with `/backport`. The action then inspects labels and creates backport PRs.

## State and Persistence Behavior

The workflow can create branches, commits, comments, and pull requests through GitHub APIs using the workflow token. It stores no local persistent artifacts.

## Dependencies and Integration Points

It integrates with GitHub Actions, PR labels, GitHub comments, and repository branch permissions. The bot-user-id filter prevents recursive comment-triggered loops.

## Risks and Edge Cases

`pull_request_target` runs with elevated token permissions, so action pinning and trust boundaries matter. The third-party action is version-pinned by tag rather than immutable SHA. If the bot user id changes because a different token/bot is used, recursion prevention may fail. Label naming must stay aligned with development docs and maintenance branch conventions.

## Test Signals

Test by merging a labeled PR in a safe repository or using a manual `/backport` comment. Also validate that unlabeled merged PRs do nothing and bot-authored comments do not retrigger.
