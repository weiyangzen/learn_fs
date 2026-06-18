# sources/object-store/minio/cmd/background-heal-ops.go

## Purpose
Implements background healing task dispatch for disk format, bucket, and object healing, including worker sizing and optional throttling based on active HTTP IO.

## Important APIs, types, and functions
- `healTask` carries bucket/object/version/options and an optional response channel.
- `healResult` carries a `madmin.HealResultItem` plus error.
- `healRoutine` owns the task channel and worker count.
- `activeListeners`, `currentHTTPIO`, `waitForLowIO`, and `waitForLowHTTPReq` support IO-aware throttling.
- `initBackgroundHealing`, `(*healRoutine).AddWorker`, `newHealRoutine`, and `healDiskFormat` run the background healer.

## Control flow
`newHealRoutine` defaults worker count to half of `GOMAXPROCS`, allows `_MINIO_HEAL_WORKERS` override, and falls back to four if the result is zero. `initBackgroundHealing` creates a background heal sequence, starts worker goroutines, and launches a new global heal sequence. Each worker selects on tasks or context cancellation, dispatches `nopHeal`, disk-format heal, bucket heal, or object heal, sends synchronous results when `respCh` is present, and otherwise updates background sequence metrics.

## State and persistence behavior
This file mutates in-memory healing metrics/state through `globalBackgroundHealRoutine` and `globalBackgroundHealState`. Actual repair persistence happens in `ObjectLayer.HealFormat`, `HealBucket`, and `HealObject`.

## Dependencies and integration points
Integrated with `ObjectLayer`, admin heal options/results from `madmin-go`, global HTTP listen/trace subscriber counts, global heal config, background heal sequence metrics, and environment configuration.

## Risks and edge cases
Worker count override can oversubscribe resources. `waitForLowIO` depends on external callers and current HTTP count excluding listeners. Async tasks without `respCh` rely on metrics for observability. `healDiskFormat` suppresses `errNoHealRequired` but returns other format-heal errors.

## Test signals
No direct tests in this subset; coverage likely comes from heal/admin integration tests.
