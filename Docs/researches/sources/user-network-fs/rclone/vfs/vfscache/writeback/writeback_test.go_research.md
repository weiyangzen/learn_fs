# sources/user-network-fs/rclone/vfs/vfscache/writeback/writeback_test.go

## Purpose
Validates the writeback scheduler's priority queue, timer, retry, cancellation, rename, duplicate, and stats behavior with controllable fake upload functions.

## APIs, Flow, And State
`newTestWriteBack` creates a scheduler with 100 ms writeback delay. `putItem` simulates an upload using channels for start, completion, and cancellation. Heap helper assertions check `onHeap`, lookup membership, and index consistency. Tests progress queued items through automatic timers, finish uploads with nil or error, and inspect whether items remain in the heap/lookup map.

## Dependencies And Integration
Uses `fs.GetConfig(ctx).Transfers` to test concurrency caps and `vfscommon.Opt` for scheduler timing. The fake `PutFn` focuses tests on scheduler state rather than remote IO.

## Risks And Test Signals
Timing-driven tests can be sensitive to slow environments, but the channel-based fake upload makes most transitions deterministic. Coverage is strong for scheduler invariants, including failure backoff, cancellation on modified updates, no cancellation for unmodified updates, queue JSON fields, `SetExpiry`, transfer-limit timer stopping, rename requeue, duplicate-name eviction, and explicit `cancelUpload`.
