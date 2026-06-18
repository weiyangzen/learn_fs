# sources/user-network-fs/rclone/lib/exitcode/exitcode.go

Source read signal: reviewed complete local file (27 lines, sha256 d175aaf79b66c36d).

Purpose: Centralizes rclone process exit status numbers.

Important APIs/types/functions: Exports constants `Success`, `UncategorizedError`, `UsageError`, `DirNotFound`, `FileNotFound`, `RetryError`, `NoRetryError`, `FatalError`, `TransferExceeded`, `NoFilesTransferred`, and `DurationExceeded`.

Control flow: No runtime flow; constants are assigned by `iota`.

State and persistence behavior: No state. Numeric values are an external CLI contract consumed by scripts and users.

Dependencies and integration points: No imports. Command-line error handling should use these constants for consistent process termination.

Risks and test signals: Reordering or inserting constants before existing ones would change public exit codes. Tests elsewhere should assert key code values if this ABI must remain stable.
