# sources/storage-engines/wiredtiger/test/packing/smoke.sh

Purpose: shell smoke driver for the packing test directory. It runs a small representative subset during check rather than every performance-oriented packing test.

Important APIs and control flow: `set -e` makes any failing command abort the script. The script invokes `$TEST_WRAPPER ./packing-test`, `$TEST_WRAPPER ./intpack-test3`, and `$TEST_WRAPPER ./int4bpack-test`.

State and persistence behavior: no persistent state is created by the script itself. It delegates all state to the executed test binaries.

Dependencies and integration points: depends on the build system producing the named executables and on `TEST_WRAPPER` being set by the test environment, commonly to inject sanitizer, timeout, or platform wrappers.

Risks: failures are coarse-grained because the script does not annotate which subtest failed beyond shell output. It intentionally excludes some directory tests, so broader packing regressions require dedicated test execution.

Test signals: a zero exit status from all three binaries is the check signal for packing smoke coverage.
