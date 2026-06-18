# sources/sync-backup/bup/dev/make-splittable-tree

## Purpose
Creates a large directory tree for split/index performance or behavior tests.

## Important APIs, Types, and Functions
Bootstraps `dev/python`, reads `BUP_SPLITTABLE_COUNT`, uses `mkdir` and empty `data` files.

## Control Flow
Requires one destination path, fails if it already exists, creates it, then creates numbered subdirectories each containing an empty file.

## State and Persistence Behavior
Writes a generated directory tree; default count is 10000.

## Dependencies and Integration Points
Used by tests/dev workflows that need many paths for splitting/indexing.

## Risks and Test Signals
Risks are large inode usage and existing target failure. Signal is exact tree shape and nonzero misuse exit.
