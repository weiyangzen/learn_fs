<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/ISSUE_TEMPLATE/config.yml -->
# sources/object-store/minio-mc/.github/ISSUE_TEMPLATE/config.yml

## Purpose
GitHub issue-template configuration for the MinIO client repository. It disables blank issues and points users to community support for questions.

## Important APIs, types, and functions
YAML keys are `blank_issues_enabled: false` and a single `contact_links` entry named MinIO Community Support with Slack URL and explanatory text.

## Control flow
GitHub reads this metadata when a user opens an issue and offers the configured support link instead of allowing an unstructured blank issue.

## State and persistence behavior
No application state. It affects repository issue intake and triage workflow.

## Dependencies and integration points
Integrates with GitHub issue templates and MinIO community support operations.

## Risks and test signals
Disabling blank issues can reduce low-quality reports but may block valid reports if no issue forms are present. Test signal is GitHub rendering the issue chooser as intended.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/ISSUE_TEMPLATE/config.yml -->
