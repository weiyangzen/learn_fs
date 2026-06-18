# sources/user-network-fs/rclone/fs/walk/walk_test.go

## Purpose
This file unit-tests the walk package's traversal, recursive listing, filtering, synthetic directory, and error behavior using mock filesystem entries.

## Important APIs, Flow, and State
The harness defines `listResult`, `listResults`, `errorMap`, and `listDirs`. `newListDirs` creates scripted expectations. `ListDir` and `ListR` simulate backend APIs, `WalkFn` validates callback arguments and returns scripted errors, and wrapper methods run `walk` or `walkR`.

Tests cover empty walks, skip behavior, not-found errors and masking, max depth, `walkNDirTree`, multi-level trees, terminal errors, `walkRDirTree`, root subpaths, max-level clipping, exclude filters, exclude-file pruning, `ListType`, direct `listR` filtering and bucket directory synthesis, and `dirMap` add/send behavior. The mock harness uses maps as call ledgers, so extra, missing, or incorrect traversal work is visible.

## Dependencies, Risks, and Test Signals
Dependencies include `mockdir`, `mockfs`, `mockobject`, `filter`, `fserrors`, and `testify`. The tests guard `ErrorSkipDir` semantics, callback error propagation, depth stopping, direct `ListR` filtering, exclude-file pruning, bucket parent synthesis, and callback content. Golden `dirtree.DirTree.String()` output and exact synthetic-directory arrays provide compact but strong signals.
