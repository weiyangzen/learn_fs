<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fsize.c -->
# sources/test-tools/stress-ng/stress-fsize.c Research

Purpose: implements `fsize`, a filesystem/OS VERIFY_ALWAYS stressor that validates file-size limit enforcement through `RLIMIT_FSIZE`, `fallocate()`, `ftruncate()`, and `SIGXFSZ`.

Important APIs/types/functions: `stress_fsize_handler()` records SIGXFSZ delivery. `stress_fsize_reported()` suppresses repeated messages for the same offset/type. `stress_fsize_boundary()` sets a file-size limit and tests allocation just below and at the boundary. `stress_fsize_max_off_t()` discovers the maximum signed `off_t`. `stress_fsize_info` exports either the stressor or an unimplemented placeholder when fallocate, RLIMIT_FSIZE, or SIGXFSZ support is missing.

Control flow: the stressor saves the original `RLIMIT_FSIZE`, computes a bounded maximum, installs the signal handler, creates and unlinks a temp file, synchronizes, then loops. Each iteration sets a small current limit, truncates to zero, confirms allocation up to the limit succeeds, confirms allocation beyond it fails with expected errors and raises SIGXFSZ, tests a random boundary, restores the original limit, then tests powers-of-two-minus-one offsets up to the max offset. It records SIGXFSZ signals per second at exit.

State and persistence: process resource limits are mutated and restored during each iteration. The temp file is unlinked immediately after opening and closed on exit. Signal counters are static process state.

Dependencies and integration: depends on stress-ng temp directory helpers, fallocate shim, signal handling, resource-limit APIs, bogo counters, metrics, and filesystem usage reporting.

Risks: resource limits are process-wide, so early fatal paths before restoration could affect the worker until process exit. Filesystem and kernel behavior around fallocate, ENOSPC, EINTR, and SIGXFSZ can vary. The signal counter is intentionally racy, acceptable for metrics but not exact.

Test signals: failures identify unexpected fallocate success, unexpected errno, missing/unexpected SIGXFSZ, or inability to truncate. A healthy run reports SIGXFSZ signals/sec and steady bogo progress. Coverage should include filesystems with and without fallocate support and constrained quota/space cases.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fsize.c -->
