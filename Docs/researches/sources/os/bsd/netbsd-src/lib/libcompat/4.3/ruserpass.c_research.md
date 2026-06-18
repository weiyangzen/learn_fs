# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.3/ruserpass.c

## Purpose
Parses `~/.netrc` to supply login/password information for legacy remote access clients such as `rexec()`.

## Behavior
Opens `$HOME/.netrc`, tokenizes keywords and values, matches `machine` or `default` entries against the requested host, handles local-domain short-name matching, fills missing login/password strings, enforces restrictive permissions for password/account entries, and parses/stores `macdef` macro definitions in static buffers.

## Dependencies
Depends on environment `HOME`, hostname/domain detection, `stat` permission checks, token parsing, fixed macro arrays, and libc warning/error helpers.

## Risks And Notes
Global parser state and macro storage are not thread-safe. Password/account entries in group/world-readable `.netrc` files are rejected. Token buffers and macro buffers are fixed-size historical limits.
