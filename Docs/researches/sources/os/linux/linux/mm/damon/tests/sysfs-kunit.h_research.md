# File Research: sources/os/linux/linux/mm/damon/tests/sysfs-kunit.h

KUnit tests for DAMON sysfs target conversion. The header is included by `sysfs.c` under `CONFIG_DAMON_SYSFS_KUNIT_TEST`, allowing it to exercise static sysfs helpers directly.

Coverage:
- Defines a local `nr_damon_targets()` helper to count runtime targets in a `damon_ctx`.
- Finds an existing PID in a caller-provided numeric range with `find_get_pid()` and `put_pid()`.
- Builds a minimal `damon_sysfs_targets` object containing one `damon_sysfs_target` with an empty regions object.
- Creates a `damon_ctx`, calls `damon_sysfs_add_targets()`, and checks that the runtime target count increases.
- Changes the sysfs target PID to another valid PID, calls `damon_sysfs_add_targets()` again, and checks that the context now has two targets.

Important behavior documented:
- `damon_sysfs_add_targets()` appends targets to the context; it does not clear existing targets before adding the new sysfs targets.
- For PID-backed operations, target addition depends on a valid `struct pid` lookup.
- Empty sysfs region configuration is allowed at this layer; backend initialization can later derive default regions.

Structure:
- The suite name is `damon-sysfs`.
- The single test case is `damon_sysfs_test_add_targets`.
- Allocation and PID-discovery failures are treated as skips rather than hard failures.
