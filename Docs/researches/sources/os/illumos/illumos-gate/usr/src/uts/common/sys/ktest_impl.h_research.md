# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ktest_impl.h

## Purpose
Defines private in-kernel data structures for the ktest facility.

## Main Interfaces
- Under `_KERNEL`:
  - `ktest_module_t`: module list node, name, suite/test counts, and suite list.
  - `ktest_suite_t`: suite list node, owning module, name, test count, and test list.
  - `ktest_test_t`: test list node, owning suite, name, function pointer, and input requirement flag.
  - `ktest_ctx_t`: runtime context with test pointer, result pointer, input buffer, and input length.

## Dependencies And Relationships
Includes `sys/ktest.h`, `sys/list.h`, and `sys/types.h`. It should only be used by the ktest implementation, not by userspace or test modules.

## Research Notes
The file explicitly states that external consumers should use `sys/ktest.h`. These structures back the opaque handles exposed in the public ktest header.
