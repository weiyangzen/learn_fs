# File Research: sources/virtualization/qemu/block/commit.c

Implements block commit, both the modern live block job path (`commit_start()`) and the older synchronous `bdrv_commit()` helper. The live job copies allocated data from an overlay chain into a base image, then drops intermediate nodes from the backing chain.

`CommitBlockJob` tracks the temporary `commit_top` filter, top/base `BlockBackend`s, base node, base overlay, on-error policy, backing-file replacement string, and whether the backing chain is frozen. `commit_iteration()` queries allocation status above the base, writes zero extents with `blk_co_pwrite_zeroes()`, copies allocated data via an aligned 512 KiB buffer, rate-limits progress, and maps I/O errors through block job error policy. `commit_run()` sizes/truncates the base if needed, allocates the buffer, loops through the image, sleeps for rate limiting, and stops on cancellation.

`commit_start()` validates distinct top/base, adjusts base writability, inserts a `commit_top` filter above top, freezes the chain down to base, adds blocker permissions for intermediate nodes, creates top/base block backends, and starts the job. `commit_prepare()` unfreezes the chain and calls `bdrv_drop_intermediate()`. `commit_abort()` removes blockers, replaces the commit filter with its backing node, and notes the consistency risk if partial writes already reached the base.

The `commit_top` filter is a dummy consistent-read provider that forwards reads to backing while allowing writes in the backing chain. The synchronous `bdrv_commit()` drains all nodes, temporarily inserts `commit_top` above the backing file, copies allocated regions, attempts to empty the source, flushes both sides, and restores read-only/backing state on cleanup.
