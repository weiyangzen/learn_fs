# `sources/test-tools/fio/.github/ISSUE_TEMPLATE/config.yml`

Purpose: Configures GitHub issue template behavior for fio.

Important settings: `blank_issues_enabled: true` permits users to open issues without a structured template. `contact_links` adds a general-questions link pointing users to the fio mailing list and notes that plain-text email is expected.

Control flow: GitHub reads this YAML when rendering the new-issue UI. It does not affect builds or runtime behavior.

State and persistence: Repository metadata only; no generated state.

Dependencies and integration: Depends on GitHub issue template schema. Integrates project support workflow with the external vger fio mailing list.

Risks and test signals: The URL is HTTP and external; if the mailing-list page changes, issue guidance degrades. Tests are mainly repository metadata validation or manual GitHub UI review.
