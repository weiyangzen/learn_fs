# sources/storage-engines/badger/.github/ISSUE_TEMPLATE/config.yml

Purpose: configures GitHub issue creation for the Badger repository by disabling blank issues and directing support questions to organization discussions.

Important data: `blank_issues_enabled: false` prevents ad hoc issue creation through the default template, and `contact_links` defines "Badger Community Support" pointing at `https://github.com/orgs/dgraph-io/discussions`.

State and persistence: this is repository metadata consumed by GitHub; it does not affect runtime code. Dependencies are GitHub's issue-template schema. Integration points are the GitHub issue UI and the Dgraph discussions space. Risks: disabling blank issues can improve issue quality but may block reports when no suitable template exists; the support URL is external to this repository and must remain valid. Test signals are repository UI checks and YAML linting.
