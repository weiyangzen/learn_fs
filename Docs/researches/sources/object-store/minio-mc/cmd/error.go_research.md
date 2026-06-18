# sources/object-store/minio-mc/cmd/error.go

Purpose: Central fatal/nonfatal error reporting, exit-status wrapping, and deprecated flag/command messaging.

Important APIs/types/functions: `causeMessage`, `errorMessage`, `fatalIf`, `fatal`, `exitStatus`, `errorIf`, `deprecatedError`, `deprecatedFlagError`, and `deprecatedFlagsWarning`.

Control flow: Fatal and nonfatal paths produce structured JSON when `globalJSON` is set, optionally adding call traces/sysinfo under `globalDebug`. Human output trims and punctuates messages, replaces details with context-canceled text when appropriate, and calls console fatal/error functions.

State and persistence: Reads global output/debug/cancellation state. No persistence.

Dependencies/integration: Used broadly across commands. Depends on `probe.Error`, `console`, `cli.ExitCoder`, and global context flags.

Risks: Fatal exits make unit tests harder. Formatting logic changes user-visible messages. `deprecatedFlagsWarning` scans args only, not normalized CLI flags.

Test signals: No direct tests in this subset.
