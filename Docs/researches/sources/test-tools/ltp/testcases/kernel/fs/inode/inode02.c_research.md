# sources/test-tools/ltp/testcases/kernel/fs/inode/inode02.c

## Purpose

`inode02.c` is the concurrent stress version of `inode01`. It forks multiple children, and each child independently creates, records, verifies, and removes a directory/file tree with configurable depth, breadth, file length, and child count.

## Important APIs, Types, and Functions

Important functions are `tree`, `generate`, `check`, `get_next_name`, `increment_name`, `mode`, `escrivez`, `term`, `massmurder`, `setup`, `anyfail`, `forkfail`, `terror`, and `instress`. Parameters `max_depth`, `max_breadth`, `file_length`, and `nchild` control the generated workload.

## Control Flow

`main` parses optional numeric arguments or defaults to depth 6, breadth 5, file length 8, and five children. It forks `nchild` workers; each worker runs `tree`, which creates `inode02.<pid>`, builds `path_list`, calls recursive `generate`, reopens the manifest, calls `check`, removes the tree, and exits with the minimum generation/check result. The parent waits for all children and reports aggregate success.

## State and Persistence Behavior

Each child owns a separate tree and manifest. Global buffers and fds are copied at fork and then child-local. `remove_string` holds the cleanup shell command for the active child.

## Dependencies and Integration Points

Uses legacy LTP, fork/wait, signal handling, directory/file syscalls, and `system("rm -rf ...")`. The Makefile defines `LINUX` for Linux includes and prototypes.

## Risks and Edge Cases

`allchild` is never populated in the visible fork loop, so `massmurder` cannot reliably signal live children. `open(path, READ)` treats fd 0 as failure. The default tree can be large and resource-heavy; `instress` assumes fork failure can be acceptable under stress. Signal handlers do non-async-safe cleanup.

## Test Signals

Pass means all child exit statuses are zero and the waited-child count matches `nchild`. Failures identify wrong child count, fork failure, generation errors, manifest read errors, file content mismatches, or directory mode problems.
