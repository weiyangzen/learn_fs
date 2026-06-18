# sources/sync-backup/restic/internal/fs/file_unix.go

Purpose: Non-Windows path, temporary file, unsupported-feature, and chmod behavior.

Important APIs: `fixpath`, `TempFile`, `isNotSupported`, and `chmod`.

Control flow and state: `fixpath` is identity. `TempFile` creates then unlinks the file so it is removed when closed. `chmod` ignores `ENOTSUP` from filesystems that cannot apply modes.

Dependencies and integration: Used by file wrappers and restore metadata. The unlink-on-open temp file pattern avoids leaving temporary files after close on Unix-like systems.

Risks: `TempFile` depends on Unix delete-while-open semantics. `isNotSupported` only recognizes `*os.PathError` wrapping `syscall.ENOTSUP`.

Test signals: Unix FIFO read tests and generic restore tests exercise these helpers indirectly.
