<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp.in -->
# sources/test-tools/strace/tests/filter_seccomp.in

## Purpose
Covers strace self-test coverage for `filter_seccomp`. Source read: 4 lines, 238 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none.

## Control Flow
process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events.

## State And Persistence Behavior
shell/table state is file based: generated scripts, logs, expected-output files, and harness variables.

## Dependencies And Integration Points
Depends on only the C library/shell runtime and local test harness. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: seccomp-BPF availability and filter installation can vary by kernel/configuration; concurrency and process ordering can make trace matching fragile. Test signals: generated `.gen.test` scripts and `gen_tests.am` are build outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter_seccomp.in -->
