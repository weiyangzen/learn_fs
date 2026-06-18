<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/checksum/checksum.go -->
# sources/user-network-fs/rclone/cmd/checksum/checksum.go

## Purpose

`checksum.go` implements `rclone checksum`, validating a destination against a SUM-format hash file.

## Important APIs, Types, and Functions

The package has a `download` flag and imports `cmd/check` for shared report flags and help. The Cobra command requires `<hash> sumfile dst:path`, parses the hash with `hash.Type.Set`, resolves the SUM file and destination with `cmd.NewFsSrcFileDst`, builds `CheckOpt` through `check.GetCheckOpt(nil, fsrc)`, and calls `operations.CheckSum`.

## Control Flow

Argument and hash validation happen before `cmd.Run(false, true, ...)`. The report writers are opened during run execution and closed after `CheckSum`.

## State and Persistence Behavior

Remote state is read-only. It may create local report files via inherited check flags. SUM file contents are read and destination object hashes or downloaded content are compared.

## Dependencies and Integration Points

It relies on `fs/hash`, `operations.CheckSum`, and shared `check` report option plumbing.

## Risks and Test Signals

Risks include unsupported hash names, malformed SUM files, nil source Fs confusion in report options, expensive `--download`, and report path truncation. Tests should cover hash validation, SUM file-as-source argument splitting, all report outputs, download mode, and error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/checksum/checksum.go -->
