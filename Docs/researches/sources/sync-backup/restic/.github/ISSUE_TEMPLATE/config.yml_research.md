# sources/sync-backup/restic/.github/ISSUE_TEMPLATE/config.yml

Purpose: GitHub issue-template configuration that redirects general support questions to the restic forum.

Control flow/state: it declares one `contact_links` entry named `restic forum` with URL `https://forum.restic.net` and explanatory text asking users not to open issues for usage questions. It has no executable logic and no persistence outside GitHub's issue UI behavior.

Dependencies/integration: consumed by GitHub Issues when rendering the new-issue page. It complements issue templates elsewhere in the repository by adding an external support route.

Risks/test signals: the only risk is stale forum URL or guidance. Validation is GitHub accepting the YAML and displaying the contact link.
