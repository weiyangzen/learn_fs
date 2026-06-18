# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.4/cuserid.c

## Purpose
Implements historical `cuserid()` compatibility API.

## Behavior
Looks up the effective UID with `getpwuid_r()`. If lookup fails, clears the caller buffer when provided and returns it. If no caller buffer is supplied, uses a static `L_cuserid` buffer. Copies the username with `strncpy()`.

## Dependencies
Depends on password database APIs, `geteuid()`, and `L_cuserid`.

## Risks And Notes
The static buffer path is not thread-safe. `strncpy()` may not NUL-terminate if the username length reaches `L_cuserid`.
