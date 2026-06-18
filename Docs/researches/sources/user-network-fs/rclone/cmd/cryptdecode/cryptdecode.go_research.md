<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cryptdecode/cryptdecode.go -->
# sources/user-network-fs/rclone/cmd/cryptdecode/cryptdecode.go

## Purpose

`cryptdecode.go` implements `rclone cryptdecode`, translating crypt remote filenames to plaintext or, with `--reverse`, plaintext names to encrypted names.

## Important APIs, Types, and Functions

`Reverse` is the flag-backed mode switch. The command validates two to eleven args, calls `fs.ConfigFs` for the crypt remote, requires backend type `crypt`, constructs a `crypt.Cipher`, and dispatches to `cryptDecode` or `cryptEncode`. Those helpers build tab-separated output lines and print once.

## Control Flow

All work happens under `cmd.Run(false, false, ...)`. Decode failures are reported per filename as "Failed to decrypt" but do not return an error; encode always returns nil.

## State and Persistence Behavior

It reads crypt config and writes stdout only. No remote calls or config writes occur.

## Dependencies and Integration Points

It integrates with `backend/crypt` cipher construction, `fs.ConfigFs`, and Cobra flags.

## Risks and Test Signals

Risks include accepting invalid config values only at cipher construction, suppressing decode errors as successful exit, tabular output parsing with filenames containing tabs/newlines, and global `Reverse` leakage. Tests should cover crypt/non-crypt remotes, decode failures, reverse mode, max argument limit, and output formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cryptdecode/cryptdecode.go -->
