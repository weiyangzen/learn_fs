# Research: sources/user-network-fs/rclone/fs/rc/jobs/job.go

## sources/user-network-fs/rclone/fs/rc/jobs/job.go

Purpose: manages synchronous/asynchronous rc jobs, job status/list/stop/group-stop endpoints, JSON job dispatch, and batch execution. APIs include `Job`, `Jobs`, `NewJob`, `OnFinish`, `GetJob`, `GetJobID`, `NewJobFromParams`, `NewJobFromBytes`, and `rcBatch`.

Control flow creates jobs with atomic IDs and process-wide `executeID`, parses special `_async`, `_config`, `_filter`, and `_group` parameters, wraps contexts with cancellation and RC markers, runs functions in goroutines or inline, records output/error/duration, notifies finish listeners, and expires finished jobs after configured durations. Batch dispatch validates input objects and runs commands sequentially or via `errgroup` with a concurrency limit. State is global: `running`, `jobID`, job maps, timers, listeners, and links into `cache.JobOnFinish`. No disk persistence. Dependencies include rc registry, fs/accounting/filter/cache, UUID, errgroup, and HTTP status shaping. Risks include global mutable job state, listener races, cancellation blocking in `Stop`, closure capture in concurrent batch loops, special-parameter mutation, context detachment for async jobs, and expiration timing. Tests are extensive.
