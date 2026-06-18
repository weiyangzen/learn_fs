# sources/test-tools/crashmonkey/code/harness/c_harness.cpp

Purpose: provides the `main()` entry point for CrashMonkey. It parses CLI options, drives the `Tester` through setup/profiling/replay phases, optionally coordinates with an external client over a Unix socket, and writes run logs.

Important APIs/control flow: options select background mode, automated checks, devices, disk size, flag device, log save/load files, mount options, dry run, permuter shared object, iterations, fs type, verbosity, replay modes, full-bio replay, and sector size. Phase 0 validates arguments, opens a background socket, constructs `Tester`, inserts cow_brd, loads the test and permuter, sets environment variables, and changes dirty-expire timing. Phase 1 creates or loads a base disk image. Phase 2 records a workload through the wrapper or loads a saved profile. Phase 3 runs random and/or in-order replay tests. Phase 4 prints stats and cleans up.

State and persistence behavior: the program creates timestamped log files, optional profile/snapshot binary logs, `run_changes` serialized user-tool data, and environment variables `MOUNT_FS` and `FILESYS_SIZE`. It mutates kernel modules, procfs settings, mounted filesystems, and cow_brd snapshots.

Dependencies and integration: depends on `Tester`, `BaseTestCase` shared libraries, `RandomPermuter.so` by default, communication socket utilities, filesystem tools, `fdisk`, root privileges, and fixed mount/device paths.

Risks: `cout << "running " << argv` prints the pointer value, not argv contents. The fs-type lowercasing loop modifies a copy of each char (`for (auto c : fs_type)`) and has no effect. `path = argv[test_case_idx]` is evaluated before confirming `test_case_idx != argc`, so missing test argument can read out of bounds. Background socket is always initialized even when not needed. Several cleanup paths return without restoring dirty-expire settings. `change_fd` may be uninitialized for checkpoint-specific child runs. Command strings and `fdisk` parsing are brittle. The `no_lvm` and `dry_run` variables are mostly unused/misleading.

Test signals: phase banners and log files show progress; socket messages signal background checkpoint workflow; final `TestSuiteResult` output gives pass/fail counts. CLI smoke tests should cover missing args, reload-log mode, dry run, background protocol, and both replay modes.
