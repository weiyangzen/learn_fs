# sources/storage-engines/wiredtiger/test/csuite/time_shift_test.sh

Purpose: this shell test checks that WiredTiger synchronization code uses monotonic time rather than realtime clock time. It runs `test_rwlock`, shifts apparent realtime backwards through libfaketime, and compares runtime against a baseline.

Important APIs and variables: it uses POSIX shell, `libfaketime`, `DONT_FAKE_MONOTONIC=1`, `taskset` on Linux, `DYLD_INSERT_LIBRARIES` on Darwin, `RW_LOCK_FILE` as an optional binary override, and `~/.faketimerc` as the libfaketime control file. `CPU_SET` defaults to `0-1`.

Control flow: the script validates the libfaketime library argument, resolves the `test_rwlock` binary, measures a normal run duration, then launches a second run under libfaketime. After five seconds it writes a negative offset equal to the baseline duration into `~/.faketimerc`, waits for the test, removes the faketime file, and computes percentage runtime change. A change of 20 percent or less passes.

State and persistence behavior: the only persistent side effect is temporary creation of `~/.faketimerc`, which is removed after the faketime run. The script changes environment variables for dynamic library injection and resets Darwin variables afterward.

Dependencies and integration points: it depends on libfaketime, a working `test_rwlock` binary, `taskset` on Linux, and OS-specific dynamic loader behavior. It is likely invoked manually or by a platform-specific test target because it alters user-level faketime configuration.

Risks and test signals: runtime comparison is sensitive to noisy hosts, CPU scheduling, too-small baseline durations, and missing taskset/libfaketime support. The pass/fail signal is the computed percentage difference and exit status.
