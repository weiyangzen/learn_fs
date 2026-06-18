# sources/sync-backup/borg/.github/FUNDING.yml Research

## Purpose

`FUNDING.yml` configures GitHub Sponsors and funding links for BorgBackup. It advertises `borgbackup` on GitHub Sponsors, Liberapay, Open Collective, and a custom support page.

## Important APIs, Types, and Functions

This is GitHub metadata, not executable application code. Keys are GitHub-recognized funding providers: `github`, `liberapay`, `open_collective`, and `custom`.

## Control Flow

There is no runtime control flow. GitHub reads this YAML file and renders funding links in repository UI.

## State and Persistence Behavior

The file is static repository configuration. It does not store secrets or mutate state.

## Dependencies and Integration Points

It integrates with GitHub's funding UI and external funding providers. The custom URL points at BorgBackup's support funding page.

## Risks and Edge Cases

Incorrect account names or a stale custom URL would send users to broken or unintended funding destinations. YAML structure is simple; syntax breakage would disable GitHub funding rendering.

## Test Signals

Validation is mostly by GitHub UI behavior or YAML linting. Link checks can verify that the custom funding URL remains reachable.
