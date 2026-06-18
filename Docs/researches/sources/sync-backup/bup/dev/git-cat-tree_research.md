# sources/sync-backup/bup/dev/git-cat-tree

## Purpose
Recursively dumps all blob contents reachable from a Git tree/object ID.

## Important APIs, Types, and Functions
Shell function `cat-item` calls `git cat-file -t`, `git cat-file blob`, and `git ls-tree`. Supports optional `--git-dir DIR`.

## Control Flow
Validates args, optionally exports `GIT_DIR`, determines root object type, recurses through tree entries, writes blob contents in tree traversal order, and errors on unexpected object types.

## State and Persistence Behavior
Read-only Git object traversal; output is concatenated blob data.

## Dependencies and Integration Points
Used by tests/dev tooling that need raw subtree content independent of checkout.

## Risks and Test Signals
Risks include parsing `git ls-tree` text with tabs/spaces and lack of blob separators. Signal is successful recursive content dump or failure on non-tree/blob.
