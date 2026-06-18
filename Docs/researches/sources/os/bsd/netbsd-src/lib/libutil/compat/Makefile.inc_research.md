# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/Makefile.inc

## Purpose
Adds compatibility sources and include paths for old `libutil` ABI entry points.

## Key Details
- Adds `.PATH: ${.CURDIR}/compat`.
- Adds include paths for adjacent libc and sys compatibility headers.
- Adds compatibility sources:
  - `compat_passwd.c`
  - `compat_loginx.c`
  - `compat_login.c`
  - `compat_parsedate.c`
  - `compat_login_cap.c`

## Dependencies and Role
- Supports old struct/time ABI compatibility by compiling wrapper functions into `libutil`.
