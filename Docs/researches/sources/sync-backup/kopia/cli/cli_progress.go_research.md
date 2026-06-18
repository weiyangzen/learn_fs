# sources/sync-backup/kopia/cli/cli_progress.go

## Purpose
Terminal progress implementation for snapshot upload workflows. It implements `upload.Progress`, spinner rendering, adaptive estimation flags, byte/file counters, and terminal-aware output throttling.

## APIs, Types, and Functions
Important APIs include types `progressFlags`, `cliProgress`; functions/methods `setup`, `Enabled`, `HashingFile`, `FinishedHashingFile`, `UploadedBytes`, `HashedBytes`, `Error`, `CachedFile`, `maybeOutput`, `output`, `spinnerCharacter`, `StartShared`, `FinishShared`, `UploadStarted`, plus more; flags progress: Enable progress output, progress-estimation-type: Set type of estimation of the data to be snapshotted, progress-update-interval: How often to update progress information, adaptive-estimation-threshold: Sets the threshold below which the classic estimation method will be used.

## Control Flow, State, and Persistence
Control flow binds flags progress: Enable progress output, progress-estimation-type: Set type of estimation of the data to be snapshotted, progress-update-interval: How often to update progress information, adaptive-estimation-threshold: Sets the threshold below which the classic estimation method will be used, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports fmt, os, strconv, strings, sync, sync/atomic, time, github.com/alecthomas/kingpin/v2, github.com/fatih/color, golang.org/x/term, plus 3 more. It integrates with Kopia repository internals such as kopia/internal/timetrack, kopia/internal/units, kopia/snapshot/upload plus external packages fmt, os, strconv, strings, sync, plus 5 more.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
