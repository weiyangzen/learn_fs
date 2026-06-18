# File Research: sources/os/bsd/freebsd-src/sbin/devd/devd.h

## Purpose
C-compatible declarations shared between the C lexer/parser and C++ daemon implementation.

## Main Elements
- Parser callback declarations for adding rule blocks, directories, pidfile, variables, and event processing statements.
- Lexer/parser entry points and `lineno`.
- Constants `PATH_DEVCTL` and `DEVCTL_MAXBUF`.

## Dependencies And Integration
Included by `parse.y`, `token.l`, and `devd.cc`.
