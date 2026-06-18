# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/fuser_runner.rs

Purpose: test harness that mounts a mock low-level filesystem with the fuser backend and unmounts it safely.

Important APIs: `Runner::start`, `driver`, `Drop`, static `LOG_INIT`, and two self-tests.

Control flow and state: `start` initializes test logging once, wraps the mock in `AsyncDropArc`, creates a temp mountpoint, spawns the fuser mount on the current Tokio runtime, waits for mock init completion, and returns a driver-capable runner. Drop explicitly calls `unmount_join` and `safe_panic!` on failure, ensuring mock expectations fail on the main thread.

Dependencies and integration: used by mkdir tests. Depends on backend fuser `spawn_mount`, `RunningFilesystem`, tempfile, async-drop utilities, and mock types.

Risks and tests: member order is important so the mount is dropped before mountpoint/mock. Self-tests verify setup and that unmet mock expectations surface as test failures.
