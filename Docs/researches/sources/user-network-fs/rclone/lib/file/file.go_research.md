# sources/user-network-fs/rclone/lib/file/file.go

Source read signal: reviewed complete local file (22 lines, sha256 9f50b4b9faabc2e2).

Purpose: Wraps platform-specific `OpenFile` with familiar `Open` and `Create` helpers.

Important APIs/types/functions: Exports `Open` and `Create`, both delegating to package variable/function `OpenFile`.

Control flow: `Open` calls `OpenFile` with `os.O_RDONLY`; `Create` opens read/write with create/truncate and mode 0666.

State and persistence behavior: Opens or creates real filesystem files; persistence is determined by caller writes and close behavior.

Dependencies and integration points: Uses `os` and integrates with Windows-specific `OpenFile` that enables delete/rename sharing.

Risks and test signals: Correctness depends on the platform `OpenFile` implementation. Tests verify open, append, read, rename-open, and delete-open semantics.
