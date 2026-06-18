# sources/sync-backup/git-lfs/script/changelog

Purpose: generates release changelog entries from merge commits or patch commits, either interactively or in an uncategorized noninteractive form.

Important APIs/functions: `commit_summary`, `revisions_in`, `noninteractive`, option handling for `--noninteractive` and `--patch`, Git commands, GitHub Pull Request API calls, `jq`, `curl`, and manual category selection.

Control flow: validates a commit range, chooses merge-only or patch revision traversal, then either prints uncategorized entries plus category headings or prompts the user to classify each revision as feature, bug, misc, or skip. `commit_summary` extracts a PR number from the commit, fetches PR metadata, strips backport prefixes, and emits a markdown bullet.

State/persistence behavior: no repository writes. Network requests depend on `.netrc` or curl auth configuration.

Dependencies/integration: feeds release notes consumed by the upload/release workflow.

Risks: assumes commits mention a single `#NNN` PR, depends on GitHub API availability and `jq`, and interactive mode is unsuitable for unattended CI.

Test signals: no direct tests. Usable output requires correct PR titles/numbers/authors and correctly categorized markdown sections.
