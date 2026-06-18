# Research: sources/storage-engines/tikv/components/test_util/src/lib.rs

## sources/storage-engines/tikv/components/test_util/src/lib.rs

Purpose: crate root and shared test setup utilities. It enables unstable `test`, exports encryption, KV generation, logging, runner, and security helpers, and defines CI setup, port allocation, temp directory selection, debug assertion formatting, and eventual polling.

Important APIs are `setup_for_ci`, `alloc_port`, `temp_dir`, `assert_eq_debug`, and `eventually`. `setup_for_ci` preloads backtraces, sets grpc polling strategy in CI, initializes logging when requested, installs panic abort hooks, checks environment variables, and enforces open file descriptor minimums. `alloc_port` uses an atomic randomized start below the Linux local port range. `temp_dir` optionally uses `TIKV_TEST_MEMORY_DISK_MOUNT_POINT`.

State is process-global: environment variables, atomic port cursor, logger/panic hooks, and temp directories returned to callers. Persistence is limited to temp dirs and optional log files initialized by logging module.

Dependencies include `backtrace`, `rand`, `tikv_util`, `tempfile`, module reexports, and standard env/thread/time. Risks include global env mutation, port allocation races with external processes, panic on low FD limits, and memory-disk path assumptions. Test signals are downstream test harness setup, helpful diff panics, and `eventually` timeout panics.
