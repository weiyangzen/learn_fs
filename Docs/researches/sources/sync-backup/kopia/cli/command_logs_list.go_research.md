# sources/sync-backup/kopia/cli/command_logs_list.go

## Purpose
Log listing command that discovers encrypted repository log sessions and prints their identifiers, sizes, timestamps, and summaries.

## APIs, Types, and Functions
Important APIs include types `commandLogsList`; functions/methods `setup`, `run`; Kingpin command(s) list: List logs..

## Control Flow, State, and Persistence
Control flow registers command(s) list: List logs., then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
