# Research: sources/user-network-fs/rclone/fs/rc/jobs/job_test.go

## sources/user-network-fs/rclone/fs/rc/jobs/job_test.go

Purpose: comprehensive tests for job lifecycle, async/sync execution, context mutation, status/list/stop endpoints, listeners, JSON dispatch, and batch behavior. It defines helper job functions for no-op, long-running, short-running, context-cancelled, and context-parameter-controlled jobs.

Control flow covers new job maps, expiration timers, IDs and execute IDs, finish state, panic recovery, `_async` output, synchronous output/error propagation, `_config`, `_filter`, `_group`, RC request markers, job status/list, async and sync stop, stopgroup, `OnFinish` for running/already-finished jobs, listener race stress, `NewJobFromParams`, `NewJobFromBytes`, batch error shaping, and concurrent batch ordering for 100 inputs. State includes reset global `jobID`, global rc call registry, global running jobs for some tests, timers, and goroutines. Dependencies include accounting groups, filters, rc calls, JSON, and testify. Risks covered are broad: races, cancellation, panic conversion, invalid paths, request/response-ineligible calls, bad input types, and concurrency ordering.
