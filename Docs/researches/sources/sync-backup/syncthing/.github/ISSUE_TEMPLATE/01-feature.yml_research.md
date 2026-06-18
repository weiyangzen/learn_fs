# sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/01-feature.yml

Purpose: GitHub issue form for feature requests. It labels new issues as `enhancement` and `needs-triage`, sets issue type `Feature`, and requires requesters to describe the desired behavior, the problem/use case, and alternatives or workarounds.

Important APIs/types/functions: issue-form fields include top-level `name`, `description`, `labels`, `type`, and three required `textarea` body entries with ids `feature`, `problem-usecase`, and `alternatives`.

Control flow: when a user chooses the feature template, GitHub renders the form, validates required fields, and creates an issue with the configured labels and type.

State and persistence behavior: no application state; submitted answers persist in GitHub issues and become triage input.

Dependencies/integration: integrates with GitHub Issues, release-note labeling, and policy/triage workflows that rely on conventional labels.

Risks/test signals: overly strict required fields may discourage reports, but they collect context needed to judge feature value. The signal is feature issues arriving with enough structured data and labels for maintainers.
