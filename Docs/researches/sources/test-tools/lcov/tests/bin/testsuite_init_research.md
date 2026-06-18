# sources/test-tools/lcov/tests/bin/testsuite_init

Purpose: legacy Bash suite initializer that creates the count file, starts the main log, and records tool/system details.

Important APIs: no arguments. It sources `bin/common`, writes `start_time` to `COUNTFILE`, redirects stdout/stderr to `LOGFILE`, and calls helper logging functions.

Control flow and persistence: discovers `TOPDIR`, prints “Starting tests”, initializes `COUNTFILE`, logs timestamp, `lcov --version`, `gcov --version`, and platform-specific CPU/memory information from `/proc`, `sysctl`, `vm_stat`, or fallback text. This prepares the shared files consumed by `test_run` and `testsuite_exit`.

Dependencies and integration: used by legacy shell runner paths and invoked by Python `runtests.py` setup for compatibility. Depends on lcov/gcov on PATH and platform commands.

Risks and test signals: missing `lcov`/`gcov` versions are logged but not explicitly fatal. Large `/proc/cpuinfo` and `/proc/meminfo` dumps can make logs noisy. Test signal is presence of initialized `test.counts` and a header section in `test.log`.
