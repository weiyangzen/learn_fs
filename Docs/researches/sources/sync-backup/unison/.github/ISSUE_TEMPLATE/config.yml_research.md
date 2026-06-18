# sources/sync-backup/unison/.github/ISSUE_TEMPLATE/config.yml

Purpose: GitHub issue-template configuration for the Unison repository.

Important fields: `blank_issues_enabled: false` disables unstructured issues. `contact_links` sends help questions and not-fully-designed feature requests to the Unison mailing-list wiki page.

Control flow: no executable control flow; GitHub consumes this YAML when rendering the new issue UI.

State/persistence: repository metadata only. It changes user workflow in GitHub but does not affect source builds.

Dependencies/integration: depends on GitHub issue template semantics and external wiki URL availability.

Risks: disabling blank issues can reduce low-quality reports but may also block useful reports if structured templates are missing or too restrictive. External mailing-list links can rot.

Test signals: manual GitHub UI validation is the relevant check; CI does not exercise this file.
