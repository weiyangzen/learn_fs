<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/check/check.go -->
# sources/user-network-fs/rclone/cmd/check/check.go

## Purpose

`check.go` implements `rclone check`, comparing source and destination trees or a checksum file against a destination without mutating either remote.

## Important APIs, Types, and Functions

Global flags drive download mode, one-way comparison, report files, and `--checkfile` hash type. `AddFlags` exposes shared report flags for other commands. `FlagsHelp` provides reusable documentation. `GetCheckOpt` builds `operations.CheckOpt`, opens report writers including stdout for `-`, and returns a close function. `commandDefinition.RunE` selects normal two-Fs checking or checksum-file mode, validates hash names, and dispatches to `operations.Check`, `CheckDownload`, or `CheckSum`.

## Control Flow

The command validates arguments, creates Fs objects, then runs under `cmd.Run(false, true, ...)`. Report writers are opened inside the run function and closed with deferred cleanup.

## State and Persistence Behavior

Remote state is read-only. Optional local report files are created/truncated. Global flag variables affect one invocation.

## Dependencies and Integration Points

It integrates with `cmd.NewFsSrcDst`, `cmd.NewFsSrcFileDst`, `fs/hash`, `fs/operations`, and shared report flags used by `checksum` and `cryptcheck`.

## Risks and Test Signals

Risks include report file leaks, nil Fs use in checksum mode, hash overlap fallback to size-only behavior, stdout report interleaving, and download-mode cost. Tests should cover report open/close failures, `--checkfile` parsing, no-common-hash logging, one-way reports, and operation error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/check/check.go -->
