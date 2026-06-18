<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/ISSUE_TEMPLATE/config.yml -->
# sources/test-tools/syzkaller/.github/ISSUE_TEMPLATE/config.yml research

Purpose: GitHub issue-template configuration for the syzkaller repository. It disables blank issues and redirects general questions to the public syzkaller mailing list.

Important APIs, types, and functions: this is declarative GitHub metadata using `blank_issues_enabled` and `contact_links`. The single contact link has `name`, `url`, and `about` fields.

Control flow: GitHub reads this file when rendering the new-issue UI. There is no local execution path.

State and persistence: it persists repository policy in source control only. The runtime state is GitHub's issue creation UI behavior.

Dependencies and integration: integrated by GitHub under `.github/ISSUE_TEMPLATE/config.yml`; the mailing-list URL is the external support integration point.

Risks: disabling blank issues may push valid bug reports away if no suitable issue form exists. The support link must remain current.

Test signals: opening the repository's new issue page should show blank issues disabled and the mailing-list contact option.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/ISSUE_TEMPLATE/config.yml -->
