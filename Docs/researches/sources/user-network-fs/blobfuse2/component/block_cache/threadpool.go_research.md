# sources/user-network-fs/blobfuse2/component/block_cache/threadpool.go

## Purpose

`threadpool.go` provides a small worker pool used by block cache to execute asynchronous block downloads and uploads with separate priority and normal queues.

## Important APIs, Types, and Functions

`ThreadPool` holds worker count, close channel, wait group, priority and normal work channels, and reader/writer callbacks. `workItem` carries the handle, block, prefetch flag, failure count, upload flag, block id, and ETag. Functions are `newThreadPool`, `Start`, `Stop`, `Schedule`, and worker method `Do`.

## Control Flow

`newThreadPool` rejects zero workers or nil reader callbacks, then sizes `priorityCh` to `count*2` and `normalCh` to `count*5000`. `Start` launches all workers and marks roughly 10 percent as priority-only workers. `Schedule` sends urgent items to `priorityCh` and normal items to `normalCh`. `Do` loops on channel selects until `close` receives a value; priority-only workers ignore `normalCh`, while normal workers service both queues. Items with `upload=true` call `writer`, otherwise `reader`.

## State and Persistence Behavior

State is in goroutines and buffered channels only. `Stop` sends one close token per worker, waits for all workers, and closes channels. No durable state is written.

## Dependencies and Integration Points

The pool depends on `sync` and `handlemap.Handle`. It is integrated by `BlockCache` for `download` and `upload` scheduling, with work item fields avoiding handle-lock deadlocks when ETags are needed inside worker callbacks.

## Risks and Edge Cases

If `writer` is nil and an upload item is scheduled, workers will panic. `Schedule` can block when queues are full. Worker select reads from closed work channels may receive nil work items if channels close before workers stop, though `Stop` sends close tokens before closing queues.

## Test Signals

`threadpool_test.go` verifies constructor validation, start/stop, urgent and normal scheduling, priority throughput, and writer callback routing.
