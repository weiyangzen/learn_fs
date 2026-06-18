# sources/sync-backup/kopia/.github/config.yml

Purpose: regex configuration for PR titles and commit messages.

Important APIs/types/functions: `PR_TITLE_REGEX` and `COMMIT_MESSAGE_REGEX` with allowed conventional types and scopes.

Control flow: static config for GitHub automation that validates naming conventions.

State and persistence: none.

Dependencies and integration points: aligns with changelog scope filters and check-pr-title workflow.

Risks: regex requires scoped conventional format and may reject valid emergency/nonstandard changes. It lacks optional breaking `!` support that workflow regex includes.

Test signals: PR title workflow enforces a related regex.
