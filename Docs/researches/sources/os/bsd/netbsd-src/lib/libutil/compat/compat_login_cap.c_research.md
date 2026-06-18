# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_login_cap.c

## Purpose
Compatibility wrappers for login class APIs that used `struct passwd50`.

## Key Details
- Wraps `login_getpwclass`.
- Wraps `setusercontext`.
- Converts `passwd50` to current `struct passwd` before calling `__login_getpwclass50` and `__setusercontext50`.

## Dependencies and Role
- Depends on `<compat/login_cap.h>` and `<compat/include/pwd.h>`.
- Preserves old ABI while delegating all real policy work to current login capability code.
