# Research: sources/sync-backup/syncthing/script/relnotes.go

## sources/sync-backup/syncthing/script/relnotes.go

Purpose: release helper that combines repository-provided release note templates with GitHub-generated release notes.

Important APIs/functions: flags `--new-ver`, `--prev-ver`, `--branch`; `additionalNotes`, `generatedNotes`, and `removeHTMLComments`; env `GITHUB_TOKEN` and optional `GITHUB_REPOSITORY`.

Control flow: validates version and token, loads note templates from `relnotes/<version>.md` while progressively stripping patch/minor suffixes, executes them with the version value, POSTs to GitHub `releases/generate-notes`, strips HTML comments, and prints note blocks separated by blank lines.

State and persistence: read-only repository files; network read from GitHub API; output to stdout.

Dependencies and integration: GitHub API version header, templates, release workflow. Risks include required token, API failures, template errors, and comment stripping regex only handling single-line comments. Test signal is release-note output and API status.
