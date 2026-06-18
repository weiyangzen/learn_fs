# sources/test-tools/crashmonkey/code/harness/Tester.h

Purpose: declares the main CrashMonkey harness class and shared error codes/timing categories for orchestrating tests.

Important APIs/types: error macros categorize failures for cloning, formatting, mounting, wrapper/cow_brd insertion, cache clearing, and partitioning. `Tester::time_stats` indexes timing buckets. Public methods cover setup, module control, wrapper logging, test/permuter class loading, snapshot operations, workload replay, profile save/load, cleanup, and result printing.

Control flow and integration: `c_harness.cpp` calls methods in phase order. `Tester` hides lower-level interactions with kernel modules and loaded shared objects while exposing enough knobs for CLI-driven operation.

State: private fields include `FsSpecific*`, device paths, loaders, dirty-expire buffer, current suite pointer, module flags/fds, sector size, logged writes, disk modification groups, timing stats, result suites, checkpoint snapshot map, and active snapshot path.

Dependencies: depends on `FsSpecific`, `Permuter`, `TestSuiteResult`, `BaseTestCase`, `ClassLoader`, `DiskMod`, and `utils`. The class is Linux-specific because of mount/ioctl/proc/sysfs operations in the implementation.

Risks: raw pointer ownership and public constant member `verbose` initialized through constructor are non-idiomatic. Many public methods require an implicit state sequence; calling them out of order can fail or corrupt runtime state. Error codes are integer macros rather than a scoped enum. Some comments mention making private fields public for speed, indicating unresolved design debt.

Test signals: interface-level tests can mock loaded classes and verify state transitions, but realistic coverage requires full harness execution.
