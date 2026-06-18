# sources/object-store/minio/cmd/admin-heal-ops.go

## Purpose
`admin-heal-ops.go` implements the in-memory state machine and traversal logic behind MinIO admin heal operations. It tracks active heal sequences by path, exposes status/result consumption, prevents overlapping heals, supports stop and force-start, tracks local disk healing state, and queues bucket/object/meta heal tasks into the background heal routine.

## Important APIs, Types, And Functions
- `healStatusSummary` constants describe lifecycle states: not started, running, stopped, and finished.
- `allHealState` is the global coordinator with a mutex, `healSeqMap` indexed by heal path, `healLocalDisks` for local disk endpoints needing or undergoing healing, and `healStatus` keyed by disk ID.
- `newHealState`, `periodicHealSeqsClean`, `getHealSequence`, `getHealSequenceByToken`, `LaunchNewHealSequence`, `stopHealSequence`, and `PopHealStatusJSON` are the main sequence-management API used by admin handlers and background heal code.
- `healSequenceStatus` is the JSON status payload containing summary, failure detail, start time, settings, and result items.
- `healSource` describes a bucket/object/version heal task plus optional no-wait and options overrides.
- `healSequence` stores a single sequence's path, reporting settings, timings, token/client identity, cancel function, status, result indexes, scanned/healed/failed counters, activity timestamp, logger context, and mutex.
- `newHealSequence`, `healSequenceStart`, `traverseAndHeal`, `healItems`, `healDiskMeta`, `healMinioSysMeta`, `healBuckets`, `healBucket`, `healObject`, `queueHealTask`, and result/counter helpers implement the traversal and task queueing flow.

## Control Flow
A handler creates a `healSequence` with validated bucket/prefix/options and passes it to `LaunchNewHealSequence`. If the request is force-started, the existing sequence on the same path is stopped first. Otherwise, launch rejects an active sequence on the same path and then rejects any active sequence whose path overlaps the new path in either direction. Once accepted, the sequence is stored in `allHealState.healSeqMap`, a client token is returned, and a goroutine starts `healSequenceStart` unless the token is the special background-healing token.

`healSequenceStart` marks the sequence running, starts `traverseAndHeal`, then waits for either traversal completion or context cancellation. Completion sets `endTime` and marks finished on nil error or stopped with failure detail on error. Cancellation marks the sequence ended and drains the traversal channel asynchronously to avoid leaking the traversal goroutine.

Traversal heals MinIO system metadata for site-wide heals, then heals either the requested bucket or all buckets sorted newest first. Bucket healing first queues a bucket-level heal task, then calls `objAPI.HealObjects` to visit object versions and invoke `healObject`. `queueHealTask` increments scanned counters, sends work to `globalBackgroundHealRoutine.tasks`, optionally returns immediately for no-wait tasks, waits for a response when needed, updates healed/failed counters, annotates quorum-loss detail, and pushes a `madmin.HealResultItem` into the status buffer when progress reporting is enabled.

Status consumption is token-gated. `PopHealStatusJSON` finds the sequence by path, validates the client token, marshals the current status, remembers the last sent result index, and clears consumed `Items` from memory. If the sequence no longer exists, it returns a synthetic finished status.

## State And Persistence Behavior
All explicit heal sequence state in this file is in memory. Completed sequences remain in `healSeqMap` for `keepHealSeqStateDuration` and are removed by `periodicHealSeqsClean`. Forced stop removes the sequence immediately after it has ended. Heal result buffering is bounded by `maxUnconsumedHealResultItems`; if clients stop consuming results for `healUnconsumedTimeout`, push operations fail with `errHealIdleTimeout`, effectively stopping traversal.

The actual healing side effects are delegated to the object layer and background heal routine. This file queues `healTask`s that can repair bucket metadata, object metadata/data, and MinIO system metadata. Local disk healing state is tracked in maps and can be updated from `healingTracker` snapshots; `getLocalHealingDisks` returns copied status suitable for background heal status responses.

## Dependencies And Integration Points
This file is tightly coupled to `admin-handlers.go` via `globalAllHealState`, `HealHandler`, and background status endpoints. It depends on `madmin-go/v3` heal types, MinIO object-layer methods (`ListBuckets`, `HealObjects`), `globalBackgroundHealRoutine.tasks`, `healingTracker`, endpoint topology, logging request info, API error conversion, `waitForLowHTTPReq`, and global distributed-mode token decoration helpers.

## Risks And Edge Cases
Concurrency is central. `allHealState` and each `healSequence` use locks, but operations such as stop wait loops and result pushing can block for long periods. `stopHealSequence` sleeps in one-second increments until `hasEnded`, so a traversal stuck inside a slow heal operation delays stop responses. `pushHealResultItem` uses a bounded buffer but waits up to 24 hours when clients do not consume results, which protects memory at the cost of pausing healing work for a very long time.

Path overlap checks use prefix matching over joined paths. This prevents many conflicts but requires path normalization to be correct before sequence creation. Background healing is special-cased to never end and not spawn a redundant goroutine. `healSequenceStart` sets cancellation summary to finished rather than stopped, which may be intentional graceful-stop semantics but can be surprising to status consumers. `queueHealTask` may silently skip no-wait tasks when the background queue is full, relying on later background healing.

## Test Signals
`admin-handlers_test.go` covers `extractHealInitParams`, which validates inputs before this state machine is entered. It does not directly test `LaunchNewHealSequence`, overlap rejection, stop behavior, result consumption, timeout behavior, or traversal. The strongest test signal for this file in the subset is therefore parameter-level validation rather than state-machine coverage.
