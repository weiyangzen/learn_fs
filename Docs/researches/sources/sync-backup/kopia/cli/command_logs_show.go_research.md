# sources/sync-backup/kopia/cli/command_logs_show.go

## Purpose
Log show command that selects log sessions, decrypts log blobs, and streams merged or selected log content through the output formatter.

## APIs, Types, and Functions
Important APIs include types `commandLogsShow`; functions/methods `setup`, `run`; Kingpin command(s) show: Show contents of the log. When no flags or arguments are specified, only the last log is shown.; arguments session-id: Log Session ID to show.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show contents of the log. When no flags or arguments are specified, only the last log is shown., accepts arguments session-id: Log Session ID to show, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, slices, github.com/pkg/errors, github.com/kopia/kopia/internal/blobcrypto, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/blobcrypto, kopia/internal/gather, kopia/repo plus external packages context, slices, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
