# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/feature_tests.h

## Purpose

`feature_tests.h` centralizes illumos feature-test macro handling for standards namespaces, large-file compilation, compiler language levels, and visibility of extension symbols.

## Main Behavior

It derives `_POSIX_C_SOURCE` from `_POSIX_SOURCE` when needed.

It defines private implementation macros such as `__XOPEN_OR_POSIX`, `_STRICT_STDC`, `_STRICT_SYMBOLS`, `_STRICT_POSIX`, `_STDC_C99`, `_STDC_C11`, `_STDC_C17`, and `_STDC_C23`.

It detects compiler C standard levels from `__STDC_VERSION__` and compiler strictness from Sun C and GCC conventions.

It makes `_LARGEFILE64_SOURCE` and `_LARGEFILE_SOURCE` visible by default in non-strict, extension, kernel, and kmemuser contexts.

It normalizes `_FILE_OFFSET_BITS`: 64-bit builds must use 64; 32-bit builds default to 32 and allow 32 or 64.

It maps `_XOPEN_SOURCE` and `_POSIX_C_SOURCE` values onto internal `_XPG3` through `_XPG8` macros, including POSIX.1-2024 / XPG8 support.

It defines `_XOPEN_VERSION` based on the detected standard level.

It controls `_LONGLONG_TYPE`, `_RESTRICT_KYWD`, `_NORETURN_KYWD`, `_C23_UNSEQ_ATTR`, and `__EXT1_VISIBLE`.

It advertises header support macros for ISO C99, C11, C++ 1998, and DTrace version 1, while leaving `__STDC_LIB_EXT1__` undefined.

## Research Notes

This header affects nearly every public/system header, including filesystem-facing APIs such as `stat`, `statvfs`, `fcntl`, `unistd`, `uio`, and time interfaces. Large-file mode and strict symbol visibility are especially important for filesystem ABI compatibility.
