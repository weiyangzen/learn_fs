<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/github.go -->
# sources/sync-backup/restic/internal/selfupdate/github.go

## Purpose
Implements GitHub release metadata and asset download helpers for self-update.

## Important APIs and Control Flow
`Release`, `Asset`, `newGitHubRequest`, `GitHubLatestRelease`, `getGithubData`, and `getGithubDataFile` are the important APIs. Requests pin Accept headers and optionally add `GITHUB_ACCESS_TOKEN` authorization. `GitHubLatestRelease` uses a 30-second timeout, fetches `/releases/latest`, decodes JSON errors when possible, validates tag names start with `v`, and derives `Version` by trimming the prefix. Asset downloads use octet-stream Accept and suffix matching.

## State, Persistence, Dependencies, and Integration
State is network response data only; no persistence. Dependencies are `net/http`, JSON, environment variables, and GitHub's release API.

## Risks and Test Signals
Risks are API shape/rate-limit changes, leaked or malformed auth headers, missing body close on some non-OK paths, and ambiguous suffix matches. Tests cover request construction with and without tokens.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/github.go -->
