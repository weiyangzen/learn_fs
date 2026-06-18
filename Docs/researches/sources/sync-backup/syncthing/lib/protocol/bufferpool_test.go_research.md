## sources/sync-backup/syncthing/lib/protocol/bufferpool_test.go

Purpose: verifies buffer-pool bucket math, panic behavior, and concurrent use.

Important tests/helpers: `TestGetBucketNumbers` and `TestPutBucketNumbers` validate bucket selection for lengths/capacities. `TestStressBufferPool` runs concurrent get/put loops. `shouldPanic` asserts misuse panics.

Control flow and state: tests interact with a fresh pool or global bucket functions and intentionally trigger invalid cases.

Dependencies and integration points: protects allocation-sensitive protocol buffering behavior.

Risks: stress test can miss rare races without the race detector. Bucket expectations must track block-size constants.

Test signals: good coverage for pool invariants and misuse detection.
