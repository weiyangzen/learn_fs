## sources/test-tools/stress-ng/stress-unlink.c

Purpose: Implements `unlink`, stressing directory entry removal, open/unlink races, hard links, sync flags, and file close ordering.

Important APIs/types/functions: `stress_unlink_info`, `stress_unlink`, `stress_unlink_exercise`, and `stress_unlink_shuffle`; uses `open`, `link`, `unlink`, `fsync`, `fdatasync`, shared mmap metrics, and multiple forked workers.

Control flow: builds 1024 randomized filenames in a temp dir, forks three child exercisers, and the parent runs the same workload. Each exerciser opens/creates files with randomized flags, occasionally creates hard links, closes one in eight files before unlinking, unlinks all in shuffled order while timing, reshuffles, and closes remaining fds.

State and persistence: temp filenames are heap allocated and cleaned; shared `stress_metrics_t` records unlink count and duration across processes; no intended persistent files remain.

Dependencies/integration: uses `core-mmap`, `core-killpid`, stress-ng temp fs helpers, and metrics.

Risks: intentionally races sibling workers on the same names, so many open/link/unlink failures are tolerated; `VERIFY_NONE` means performance and cleanup are stronger signals than semantic verification.

Test signals: metric `unlink calls per sec`; bogo increments only in parent exercise loop.
