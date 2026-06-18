# File Research: sources/virtualization/libnbd/lib/test-fork-safe-assert.c

Unit test driver for `NBD_INTERNAL_FORK_SAFE_ASSERT`.

Flow:
- Disables core dumps via `setrlimit(RLIMIT_CORE)` and, when available, `prctl(PR_SET_DUMPABLE, 0)`.
- Forces assertions on by undefining `NDEBUG`.
- Defines `TRUE` and `FALSE` to verify macro stringification.
- Calls assert on TRUE, then on FALSE; expected outcome is abort with a diagnostic naming `FALSE`.

Interactions:
- Uses `internal.h` fork-safe assertion helper from `utils.c`.
- Paired with `test-fork-safe-assert.sh`.

Research notes:
- Test intentionally aborts; shell wrapper validates signal and stderr.
