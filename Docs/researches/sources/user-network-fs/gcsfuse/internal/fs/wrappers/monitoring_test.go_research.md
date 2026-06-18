<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring_test.go

Purpose: unit coverage for filesystem error category classification used by monitoring metrics.

Important APIs/types/functions: `TestFsErrStrAndCategory` table-driven parallel test; representative expected category constants such as `errDirNotEmpty`, `errFileExists`, `errInvalidArg`, `errInterrupt`, `errNetwork`, `errPerm`, and `errTooManyFiles`.

Control flow: each subtest calls `categorize` with either a generic error or a selected `syscall.Errno` and asserts the expected `metrics.FsErrorCategory`.

State and persistence behavior: stateless and parallel-safe.

Dependencies and integration points: validates a subset of categories used by `recordOp` in `monitoring.go`, using generated metrics category attributes.

Risks: the test samples categories rather than every errno in the switch. It does not verify operation count/latency recording or `ReadBlockSizes`.

Test signals: confirms fallback generic errors classify as IO and representative syscall values map to intended low-cardinality metric categories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring_test.go -->
