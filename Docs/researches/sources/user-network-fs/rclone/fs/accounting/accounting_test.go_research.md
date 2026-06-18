<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_test.go -->
# sources/user-network-fs/rclone/fs/accounting/accounting_test.go

## Purpose

`accounting_test.go` validates the per-transfer `Account` reader and stream-wrapper behavior.

## Important APIs, Types, and Functions

Tests cover `newAccountSizeName`, `WithBuffer`, `GetReader`, `UpdateReader`, `Read`, `WriteTo`, `String`, `Accounter`/`UnWrap`, max-transfer hard cutoff, context cancellation, `shortenName`, and optional `Seek`, `ReadAt`, and combined wrappers through custom test readers.

## Control Flow

Each test constructs a `StatsInfo` and in-memory readers, wraps them in an account, drives reads/writes/seeks, and asserts byte counters, errors, and wrapper behavior. Global config fields such as `MaxTransfer` and `CutoffMode` are saved and restored around limit tests.

## State and Persistence Behavior

All state is process-local. Tests intentionally exercise global config mutation, account goroutines, async buffers, and stats in-progress maps; correct `Close`/`Done` handling is part of leak prevention.

## Dependencies and Integration Points

It integrates with `asyncreader`, `readers.NewPatternReader`, `fserrors`, `fs.ConfigInfo`, and the accounting transfer/stat machinery.

## Risks and Test Signals

The suite signals byte-accurate accounting across Reader, WriterTo, ReaderAt, Seeker, and wrapping modes. Watch for race detector failures, goroutine leaks, and changed max-transfer semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_test.go -->
