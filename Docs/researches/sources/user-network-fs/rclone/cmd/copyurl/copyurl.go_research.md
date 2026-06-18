<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyurl/copyurl.go -->
# sources/user-network-fs/rclone/cmd/copyurl/copyurl.go

## Purpose

`copyurl.go` implements `rclone copyurl`, streaming HTTP(S) URL content directly to a remote object, stdout, or a batch of URLs from CSV.

## Important APIs, Types, and Functions

Flag globals control auto filename, Content-Disposition filename, printed filename, stdout, no-clobber, and CSV mode. `run` handles a single URL, selecting stdout, destination directory, or destination file and calling `operations.CopyURLToWriter` or injectable `copyURL`. `runURLS` reads a CSV, rejects stdout/print-filename combinations, opens destination Fs, and uses `errgroup` with `ci.Transfers` plus `errcount` to copy entries concurrently.

## Control Flow

The Cobra command validates one or two args and dispatches under `cmd.Run(true, true, ...)`. CSV rows with one field auto-name; two fields use explicit relative filenames.

## State and Persistence Behavior

It creates remote destination objects or writes URL bytes to stdout. CSV mode reads a local file and may partially complete when some rows fail.

## Dependencies and Integration Points

It integrates with `operations.CopyURL`, `CopyURLToWriter`, Fs destination helpers, transfer concurrency config, CSV parsing, errgroup cancellation context, and rclone logging.

## Risks and Test Signals

Risks include closure capture over CSV loop variables in concurrent goroutines, partial batch success, path traversal in CSV filenames, global flag leakage in tests, stdout mutation when destination is `-`, and no-clobber race behavior. Tests should cover arg validation, auto/header filenames, CSV concurrency and aggregate errors, incompatible flags, destination path joining, and copyURL injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyurl/copyurl.go -->
