# sources/user-network-fs/blobfuse2/component/block_cache/blockpool.go

## Purpose

`blockpool.go` implements a bounded pool of preallocated `Block` objects for the block cache. It limits memory consumption, separates priority and normal block availability, and asynchronously zeroes released buffers before reuse.

## Important APIs, Types, and Functions

`BlockPool` owns `blocksCh`, `priorityCh`, `zeroBlock`, `resetBlockCh`, `wg`, `blockSize`, and `maxBlocks`. Public functions are `NewBlockPool`, `Terminate`, `Usage`, `MustGet`, `TryGet`, and `Release`; helper functions are `releaseBlock` and the background method `resetBlock`.

## Control Flow

`NewBlockPool` validates `blockSize` and `memSize`, computes `blockCount`, reserves 10 percent of blocks for `priorityCh`, keeps the final block as a zero-filled template, and starts the reset goroutine. `MustGet` waits up to five seconds for either priority or normal blocks, preferring the select cases as written, then calls `ReUse`. `TryGet` only takes from `blocksCh` and returns nil if normal capacity is empty. `Release` sends blocks to the reset channel or deletes them if reset backlog is full. `resetBlock` copies `zeroBlock.data` into each released block and returns it first to `priorityCh`, then to `blocksCh`, deleting it if both are full.

## State and Persistence Behavior

All state is process-local and channel-backed. Memory is mmap-backed through `AllocateBlock`; `Terminate` closes reset processing, waits for the goroutine, closes free channels, deletes the zero block, and drains/deletes remaining pooled blocks. `Usage` counts blocks missing from free and reset channels, so the reserved zero block contributes to usage.

## Dependencies and Integration Points

The pool depends on `Block` allocation/deletion from `block.go`, `sync.WaitGroup`, `time`, and Blobfuse logging. `BlockCache` uses the pool to bound memory for read/write blocks.

## Risks and Edge Cases

`releaseBlock` reads from closed channels until it receives nil, which works for closed channels but would block if called on an open empty channel. `MustGet` can wait five seconds in tests or callers when exhausted. `TryGet` ignores priority blocks, so priority capacity is not available to nonblocking normal callers. `Release` accepts any `*Block`; nil or already deleted blocks would panic later in `resetBlock`.

## Test Signals

`blockpool_test.go` covers invalid config, allocation layout, usage percentages, exhaustion behavior, zeroing after release, and cleanup after `Terminate`.
