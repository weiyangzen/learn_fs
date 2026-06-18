<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/checkdir.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/checkdir.go

Purpose: directory content assertion helper for tests.

Important APIs, types, and functions: defines `FileInfoCheck`, `checkDirError`, and `CheckDir`.

Control flow: `CheckDir` reads a directory, builds a missing set from expected names, stats each entry, applies an exact-name or wildcard `""` checker, records unexpected entries, and returns detailed errors for missing/extra items.

State and persistence behavior: reads filesystem state only; no mutation.

Dependencies and integration points: uses `os.ReadDir` and `os.FileInfo`, intended for FUSE integration tests.

Risks and test signals: `Buffer.Bytes`-style aliasing is not present, but returned errors expose map ordering nondeterminism. Tests should cover missing, extra, wildcard, and checker failure cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/checkdir.go -->
