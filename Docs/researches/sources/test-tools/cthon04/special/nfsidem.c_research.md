# sources/test-tools/cthon04/special/nfsidem.c

## Purpose
runs an idempotency sequence of mkdir, create, chmod, rename, link, symlink, unlink, rmdir, and failed lookup to catch lost or replayed NFS replies.

## Important APIs, Types, and Functions
`main()` builds path globals `DIR`, `FOO`, `BAR`, `SBAR`, `TBAR`, `LBAR`, message `str`, and uses `stat()` for type/mode/size validation.

## Control Flow and State
For each count, it creates a test tree, writes a message, chmods it, renames into a subdir, optionally hard-links and no-op renames, optionally symlinks, validates a selected path, removes all names and directories, and verifies the top directory no longer exists.

## Persistence and Dependencies
persistent state is the temporary tree, which may remain on failure; final exit code is current `errno`. Dependencies: POSIX directory/file/link/symlink APIs and platform support for hard/symbolic links.

## Integration Points, Risks, and Test Signals
Integration is NFS duplicate request/idempotency coverage. Risks are fixed-length path buffers, unsupported links signaled only by `EOPNOTSUPP`, BSD workaround, and cleanup breakage on partial failure. Signals are exit zero after all loops and final `ENOENT` lookup.
