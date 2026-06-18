<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/acutest/acutest.h -->
# sources/user-network-fs/mergerfs/vendored/acutest/acutest.h

## Purpose
This is a single-header C/C++ unit test framework vendored into mergerfs. Test translation units define `TEST_LIST` as an array of `{name, function}` entries and include this header; unless `TEST_NO_MAIN` is set, the header supplies the whole test runner including `main`. It exposes assertion, case labeling, skip, message, dump, and optional C++ exception-checking macros while keeping implementation symbols private with `acutest_*_` names.

## Important APIs, Types, And Control Flow
Public macros include `TEST_LIST`, `TEST_CHECK`, `TEST_CHECK_`, `TEST_ASSERT`, `TEST_ASSERT_`, `TEST_EXCEPTION`, `TEST_CASE`, `TEST_MSG`, `TEST_DUMP`, `TEST_SKIP`, plus optional `TEST_INIT` and `TEST_FINI` hooks. Internal types include `acutest_test_`, `acutest_test_data_`, and `enum acutest_state_` with selected, need-to-run, excluded, success, failed, and skipped states. `main` counts `acutest_list_`, parses command-line options, selects tests by exact/word/substr match, decides whether to fork or run inline, runs each test through `acutest_run_`, prints summary, optionally emits XUnit XML, and returns failure if any test failed.

## State And Persistence
The runner maintains static process state for argv0, test metadata, verbosity, TAP/color/timer modes, current test/case, failure counts, skip reason, XML file handle, child-worker index, and `setjmp` abort recovery. Persistence is limited to stdout/stderr output and optional XML output opened by `--xml-output=FILE`; no repository state is modified.

## Dependencies And Integration Points
The header depends on the C runtime and conditionally on POSIX fork/wait/signal/timers, Linux `/proc/self/status`, Windows process/console/SEH APIs, macOS `sysctl`, C++ exceptions, and Valgrind's `RUNNING_ON_VALGRIND` when `<valgrind.h>` is available. It integrates with mergerfs tests by compiling into test binaries, and its child-process mode isolates crashing tests on Unix/Windows where available.

## Risks And Test Signals
Risks include command-line quoting on Windows child re-exec, static global state making nested/concurrent runner use unsuitable, abort paths skipping normal cleanup, `TEST_SKIP` reading the last byte of an empty formatted reason, TAP verbosity constraints, and XML escaping not being applied to test names. Test signals are direct: compile test binaries with and without `TEST_NO_MAIN`, run `--list`, selected and excluded tests, `--no-exec`, TAP, timers, skipped tests, assertion failures, crash isolation, and `--xml-output` generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/acutest/acutest.h -->
