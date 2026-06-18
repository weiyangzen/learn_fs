# sources/sync-backup/kopia/snapshot/upload/upload_estimator.go

## Purpose
Provides background data-size estimation for directory uploads so progress UIs can show expected file count and total bytes before or while upload work proceeds.

## Important APIs, Types, and Functions
`EstimationDoneFn`, `EstimationStarter`, `EstimationController`, and `Estimator` define the small control surface. `NoOpEstimationController` handles disabled estimation. `NewEstimator` creates an `estimator` with `EstimationParameters`, logger, root directory, policy tree, wait group, cancel function, and injectable `VolumeSizeInfoFn`. `WithVolumeSizeInfoFn` supports tests. `StartEstimation`, `Cancel`, `Wait`, `doRoughEstimation`, and `doClassicEstimation` implement the logic.

## Control Flow
`StartEstimation` is idempotent once started. It launches one goroutine with a cancelable context. Rough and adaptive modes first call volume-size information; failures or adaptive file counts below threshold fall back to classic scanning. Classic mode calls `Estimate` with a `scanResults` collector. The callback is always invoked with the last computed values, including zeroes after cancellation/failure.

## State and Persistence Behavior
No persistent repository state is written. Internal state is the active cancel function and wait group. Estimation reads filesystem metadata and policy ignore rules. `Wait` clears `cancelCtx`; `Cancel` cancels and clears it if active.

## Dependencies and Integration Points
Uses `internal/volumesizeinfo` for rough estimates, `Estimate` from upload scanning code for classic estimates, and `logging` for debug/warn messages. `Uploader.startDataSizeEstimation` wires it to `Progress.EstimationParameters` and `Progress.EstimatedDataSize`.

## Risks
Rough estimation returns volume-wide used size and file count, which can overestimate a subtree. `Cancel` sets `cancelCtx` nil before the goroutine completes, so callers should still call `Wait`. Fallback behavior makes rough-estimation failures non-fatal, but it can perform an expensive full scan. Unsupported/unknown estimation type effectively returns zero values unless a caller constrains inputs.

## Test Signals
`upload_estimator_test.go` covers classic, rough, rough fallback, adaptive rough/classic paths, volume-info failure fallback, context cancellation, explicit cancel, and ignore policy filtering.
