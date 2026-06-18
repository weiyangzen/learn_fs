# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/testdata/toolkit_functional_test.c

## Purpose
Functional C test for `race_toolkit.h` primitives.

## Important APIs, Types, and Functions
Defines `test_wait_on_signal`, `test_event`, `test_setup_uffd`, `test_pin_to_cpu`, `test_timer`, thread entry points, and `main`.

## Control Flow
`main` enables unbuffered I/O, pins to CPU 0, starts a thread blocked on spin-wait and releases it, starts a futex event waiter and sets it, attempts userfaultfd registration with privilege-aware skip cases, and verifies monotonic timer duration.

## State and Persistence Behavior
Uses process-local globals, threads, mmap memory, userfaultfd fd, and temp kernel resources. No file persistence.

## Dependencies and Integration Points
Compiled and executed by `toolkit_test.go` with `-pthread` and include path to the toolkit package.

## Risks and Test Signals
Timer thresholds can be sensitive on slow hosts; userfaultfd may be unavailable and is skipped only for EPERM/ENOSYS. Provides strong compile/run signal for toolkit primitives.
