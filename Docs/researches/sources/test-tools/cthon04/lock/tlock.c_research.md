# sources/test-tools/cthon04/lock/tlock.c

## Purpose
`tlock.c` is the Connectathon record-locking stress test. It exercises POSIX `fcntl()` byte-range locks or System V `lockf()` locks across a synchronized parent/child pair, including whole-file locks, single-byte ranges, end-of-file/large-offset ranges, lock splitting, process death, close semantics, optional mmap interaction, optional mandatory locking, CIFS exclusions, and lock/I/O rate measurements.

## Important APIs, Types, and Functions
Important entry points are `main()`, `initialize()`, `runtests()`, `test1()` through `test15()`, `test()`, `lockf2fcntl()`, `report()`, `read_testfile()`, `write_testfile()`, `rate()`, and `iorate()`. Compile-time switches include `USE_LOCKF`, `LARGE_LOCKS`, `LF_SUMMIT`, `MMAP`, `MACOSX`, and protocol/errno conditionals. Shared state includes `maxeof`, `testfile`, `testfd`, synchronization pipes, parent/child PIDs, counters, and error expectation globals.

## Control Flow and State
`main()` parses options, computes the test file path, creates three pipes, forks one child, and runs the selected test set for each pass. Tests alternate control between parent and child with one-byte pipe messages so one process can establish locks while the other probes, blocks, writes, kills a subchild, or verifies release behavior. The `test()` wrapper converts lock requests to either `lockf()` or `fcntl()` calls and records PASS/WARN/FATAL outcomes.

## Persistence and Dependencies
Persistent effects are limited to temporary `lockfile<pid>` files, child processes, pipes, optional memory mappings, and timing counters; `testexit()` attempts to unlink the file and kill/wait for the peer on failure. Dependencies: standard C/POSIX headers, `fcntl`, `lockf`, `lseek`, `ftruncate`, `fork`, `kill`, `wait`, `times`, `mmap` when enabled, NFS protocol-version assumptions, and the lock test Makefile.

## Integration Points, Risks, and Test Signals
Integration is through `lock/runtests` and the top-level Cthon lock suite. Risks are high around timing sleeps, platform-specific errno expectations (`EACCES` versus `EAGAIN`, `EOVERFLOW` versus `EINVAL`), destructive cleanup if `filepath` is wrong, unguarded pipe/fork failures, and mandatory locking assumptions that many modern systems ignore. Test signals are zero failures over all selected passes, expected warnings only for documented semantics differences, successful parent/child exclusion data checks, rate output, and clean unlink/child termination.
