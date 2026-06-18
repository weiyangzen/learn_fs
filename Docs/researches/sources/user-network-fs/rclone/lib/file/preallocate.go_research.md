# sources/user-network-fs/rclone/lib/file/preallocate.go

Source read signal: reviewed complete local file (6 lines, sha256 60512e528574d12f).

Purpose: Defines the shared preallocation disk-full sentinel.

Important APIs/types/functions: Exports `ErrDiskFull`.

Control flow: No runtime flow.

State and persistence behavior: No state. Platform implementations wrap OS-specific ENOSPC/disk-full errors with this value.

Dependencies and integration points: Used by Linux and Windows `PreAllocate` implementations and by callers that want to distinguish no-space from other allocation failures.

Risks and test signals: Callers should use `errors.Is` only if platform wrappers preserve identity; current implementations return the sentinel directly for recognized disk-full cases.
