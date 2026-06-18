# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sigwaitinfo.c

## Purpose
Implements `sigwaitinfo` via `sigtimedwait`.

## Key Elements
Weak-aliases `sigwaitinfo` to `_sigwaitinfo`; calls `sigtimedwait(set, info, NULL)`.

## Dependencies
Uses `<signal.h>` and the libc `sigtimedwait` wrapper.

## Behavior/Risks
Thin adapter; inherits timeout-free blocking behavior from `sigtimedwait`.
