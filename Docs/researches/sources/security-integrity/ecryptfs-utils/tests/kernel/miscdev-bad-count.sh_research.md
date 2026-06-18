## sources/security-integrity/ecryptfs-utils/tests/kernel/miscdev-bad-count.sh

Purpose: Shell wrapper for an eCryptfs misc-device regression reproducer linked to LKML 2012-01-11. It ensures kernel eCryptfs support is present, runs the compiled `miscdev-bad-count/test` probe, and propagates its status.

Important APIs and functions: sources `../lib/etl_funcs.sh`, calls `etl_load_ecryptfs`, installs `test_cleanup` trap, and executes `${test_script_dir}/miscdev-bad-count/test`. Control flow is minimal: initialize `rc=1`, load eCryptfs or exit, run the C test, store `$?`, and exit through the trap.

State and persistence: No mount or key state is created; only shell `rc` and trap state. Dependencies are bash, `modprobe`/`/proc/filesystems` behavior through `etl_load_ecryptfs`, `/dev/ecryptfs`, and the sibling C binary. Integration point is the kernel test harness `run_tests.sh`, which treats the script exit code as pass/fail. Main risk is environment sensitivity: if eCryptfs cannot load or the misc device is absent, this reports failure unrelated to the bad-count bug.
