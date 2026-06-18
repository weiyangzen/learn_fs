# sources/sync-backup/kopia/.github/workflows/check-pr-title.yml

Purpose: PR title convention enforcement workflow.

Important APIs/types/functions: trigger on opened/edited/synchronize/reopened pull requests, `deepakputhraya/action-pr-title`, and regex for conventional type/scope with optional breaking `!`.

Control flow: action validates PR title against the regex.

State and persistence: no runtime state.

Dependencies and integration points: scopes should align with changelog config and `.github/config.yml`.

Risks: action is pinned to a SHA but no version comment; regex drift from other config can create inconsistent acceptance.

Test signals: workflow pass/fail on PRs.
