# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/null.h

## Purpose

`null.h` centralizes the illumos definition of `NULL` across C, pre-C++11 C++, C++11 and later, and LP64/ILP32 modes.

## Main Interfaces

The header includes `sys/feature_tests.h` and only defines `NULL` if it is not already defined.

For C, `NULL` is `((void *)0)` to satisfy POSIX.1-2008. For C++11 and later, it is `nullptr`. For older C++, it is an integral zero constant: `0L` on LP64 and `0` otherwise.

## Runtime Use

There is no runtime behavior. The value affects compile-time overload resolution and pointer/null conversions.

## Dependencies

Depends on feature-test and compiler macros: `__cplusplus` and `_LP64`.

## Risks and Invariants

The split definitions are intentional. Changing the C++ form can affect overload resolution; changing the C form can break POSIX expectations.
