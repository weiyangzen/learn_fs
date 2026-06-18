# sources/user-network-fs/rclone/lib/kv/internal_test.go

Source read signal: reviewed complete local file (68 lines, sha256 ea42015a2c824eb5).

Purpose: Tests concurrency and global shutdown behavior of the supported KV implementation.

Important APIs/types/functions: `TestKvConcurrency` and `TestKvExit`.

Control flow: `TestKvConcurrency` starts the same facility from multiple goroutines, asserts one shared DB with multiple refs, then stops it repeatedly and checks the final inactive error. `TestKvExit` starts several facilities with increasing refs and verifies `Exit` clears the map.

State and persistence behavior: Mutates package global `dbMap` and may create cache DB files under the configured cache directory; test startup removes empty test leftovers in `Start`.

Dependencies and integration points: Uses `context`, `sync`, `fmt`, and `testify`.

Risks and test signals: Good coverage for reference counting and global map cleanup. It does not perform actual bucket read/write operations or timer expiry tests.
