# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/login_cap.h

## Purpose
Compatibility declarations for login capability functions involving `struct passwd50`.

## Key Details
- Forward declares `struct passwd` and `struct passwd50`.
- Declares public compatibility names:
  - `login_getpwclass(const struct passwd50 *)`
  - `setusercontext(login_cap_t *, struct passwd50 *, uid_t, u_int)`
- Declares current-version internal aliases:
  - `__login_getpwclass50`
  - `__setusercontext50`

## Dependencies and Role
- Header glue for `compat_login_cap.c`.
