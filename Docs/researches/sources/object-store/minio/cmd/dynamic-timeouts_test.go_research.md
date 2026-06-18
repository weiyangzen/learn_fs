<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/dynamic-timeouts_test.go -->
## sources/object-store/minio/cmd/dynamic-timeouts_test.go

Purpose: This file validates the adaptive behavior and concurrent safety expectations of `dynamicTimeout`.

Important APIs and functions: Tests include `TestDynamicTimeoutSingleIncrease`, `TestDynamicTimeoutDualIncrease`, `TestDynamicTimeoutSingleDecrease`, `TestDynamicTimeoutDualDecrease`, `TestDynamicTimeoutManyDecreases`, `TestDynamicTimeoutConcurrent`, `TestDynamicTimeoutHitMinimum`, `TestDynamicTimeoutAdjustExponential`, and `TestDynamicTimeoutAdjustNormalized`. Helper `testDynamicTimeoutAdjust` logs a full adjustment window using a random duration function.

Control flow: Increase tests fill one or two full log windows with failures and assert the timeout grows. Decrease tests fill windows with 20-second successes against a one-minute timeout and assert timeout shrinks; repeated decrease tests assert continued movement. The many-decrease and hit-minimum tests repeatedly log successes and check eventual convergence above the success duration or exactly at the configured minimum. The concurrent test starts one goroutine per `GOMAXPROCS`, logs many random successes, reads `Timeout`, and panics if it escapes the expected min/max range. Randomized tests seed the global RNG and feed exponential or normal distributions through the helper, treating durations at or above one minute as failures.

State and persistence behavior: Tests exercise only in-memory timeout state. They are sensitive to the constants in `dynamic-timeouts.go`, especially log size and adjustment thresholds.

Dependencies and integration points: The file depends on `math/rand`, `runtime`, `sync`, `testing`, and `time`. It directly tests `newDynamicTimeout`, `LogSuccess`, `LogFailure`, and `Timeout`.

Risks: The concurrent test is most valuable when run with the Go race detector; without `-race`, it mainly checks gross timeout bounds. Randomized tests use fixed seeds but still assert only broad direction. The tests do not cover `newDynamicTimeoutWithOpts`, `RetryInterval`, invalid constructor panics, negative success durations, or the 24-hour cap.

Test signals: The file gives good confidence in core adjustment direction, minimum enforcement, and basic concurrent robustness for expected workloads.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/dynamic-timeouts_test.go -->
