# sources/user-network-fs/rclone/lib/file/preallocate_other.go

Source read signal: reviewed complete local file (23 lines, sha256 ddb844a934195412).

Purpose: Stub implementation of file preallocation and sparse-file marking for platforms other than Windows and Linux.

Important APIs/types/functions: Defines `PreallocateImplemented=false`, `PreAllocate`, `SetSparseImplemented=false`, and `SetSparse`.

Control flow: Both functions return nil without modifying the file.

State and persistence behavior: No state changes; preallocation is explicitly a no-op.

Dependencies and integration points: Uses `os` for file type. Build tag excludes Windows and Linux.

Risks and test signals: Callers must check implementation constants if behavior matters. Silent no-op is intentional for unsupported platforms.
