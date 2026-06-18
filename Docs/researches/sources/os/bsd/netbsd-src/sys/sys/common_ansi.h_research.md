# File Research: sources/os/bsd/netbsd-src/sys/sys/common_ansi.h

## Scope

Defines internal typedef source macros for fundamental ANSI/POSIX types shared by standard headers.

## APIs And Behavior

- Requires compiler predefined `__PTRDIFF_TYPE__`, `__SIZE_TYPE__`, `__WCHAR_TYPE__`, and `__WINT_TYPE__`.
- Includes machine integer types.
- Defines `_BSD_CLOCK_T_`, `_BSD_PTRDIFF_T_`, `_BSD_SSIZE_T_`, `_BSD_SIZE_T_`, `_BSD_TIME_T_`, `_BSD_CLOCKID_T_`, `_BSD_TIMER_T_`, `_BSD_SUSECONDS_T_`, `_BSD_USECONDS_T_`, `_BSD_WCHAR_T_`, and `_BSD_WINT_T_`.

## Dependencies

- Includes `sys/cdefs.h` and `machine/int_types.h`.

## Risks And Invariants

- Standard headers consume and undef these macros to avoid duplicate typedefs.
- Type selections are ABI-sensitive, especially `time_t`, `size_t`, and pointer-difference types.
