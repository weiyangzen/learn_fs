# sources/sync-backup/bup/dev/subtree-hash

## Purpose
Finds the Git tree hash for a path within a root tree hash.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses bup `options`, `argv_bytes`, `git ls-tree -z`, and byte-stream stdout.

## Control Flow
Parses `ROOT_HASH [PATH_ITEM...]`, iteratively lists the current tree, finds the named child entry, replaces the current tree hash with the child hash, and prints the final hash. If a path item is missing, prints an error and exits 1.

## State and Persistence Behavior
Read-only Git object lookup.

## Dependencies and Integration Points
Used by tests/dev scripts that need to verify tree identities inside bup/Git repositories.

## Risks and Test Signals
Risks include assuming path items are tree objects and parsing specific `git ls-tree` format. Signal is final hash on stdout or path-not-found failure.
