# sources/sync-backup/bup/dev/data-size

## Purpose
Reports total apparent byte size of files under one or more paths for tests and dev diagnostics.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses `bup.compat.get_argvb`, `os.walk`, `os.path.getsize`, and `isdir`.

## Control Flow
Iterates byte paths from argv, recursively sums regular file sizes for directories, directly sums file sizes for non-directories, and prints the total.

## State and Persistence Behavior
Read-only filesystem traversal; no persistence.

## Dependencies and Integration Points
Used where tests need byte-exact apparent data size independent of shell glob encoding.

## Risks and Test Signals
Risks include walk errors raising, symlink/file type behavior inherited from `os.walk`, and concurrent changes. Signal is exact integer output.
