# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_release_latency.cc

## Purpose
This minimal latency test measures the cost of `obj_ops->release` on the per-test root object. It exists as a narrow microbenchmark for the FSAL handle release path.

## Important APIs, Types, And Functions
`ReleaseEmptyLatencyTest` inherits setup and teardown entirely from `gtest::GaneshaFSALBaseTest`. `SIMPLE` calls `test_root->obj_ops->release(test_root)`. `LOOP` repeats that call one million times and prints average nanoseconds per release with `timespec_diff`.

## Control Flow, State, And Persistence
No additional filesystem objects are created beyond the base fixture's test root. The measured call is unusual because it invokes `release` repeatedly on `test_root`, while base teardown later calls `unlink` and `put_ref` on the same object. The file explicitly notes that release cannot be bypassed.

## Dependencies And Integration Points
The test depends on the FSAL object operation table and shared Ganesha fixture. It parses the standard config/log/debug/export/session/event-list/profile options but does not use LTTng or profiler hooks directly.

## Risks And Test Signals
Repeatedly calling a release-style method on the same object can be dangerous if the operation mutates reference state, invalidates cached resources, or is not idempotent. The test signal is only that the process survives and prints timing; there is no status return or invariant assertion for `release`.
