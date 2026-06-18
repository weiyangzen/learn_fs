# sources/sync-backup/kopia/cli/command_logs_session.go

## Purpose
Shared log session discovery and filtering support for log commands. It parses all/latest/age selectors and filters repository log blob sessions.

## APIs, Types, and Functions
Important APIs include types `logSessionInfo`, `logSelectionCriteria`; functions/methods `setup`, `any`, `filterLogSessions`, `getLogSessions`, `filterLogSessions`; flags all: Show all logs, latest: Include last N logs, by default the last one is shown, younger-than: Include logs younger than X (e.g. '1h'), older-than: Include logs older than X (e.g. '1h').

## Control Flow, State, and Persistence
Control flow binds flags all: Show all logs, latest: Include last N logs, by default the last one is shown, younger-than: Include logs younger than X (e.g. '1h'), older-than: Include logs older than X (e.g. '1h'), then runs through a test/helper flow. The implementation iterates blob storage. State and persistence: touches encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, strconv, strings, time, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/internal/clock, github.com/kopia/kopia/internal/repodiag, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/internal/clock, kopia/internal/repodiag, kopia/repo/blob plus external packages context, sort, strconv, strings, time, plus 2 more.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
