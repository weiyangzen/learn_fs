# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sigqueue.c

## Purpose
Implements `sigqueue` in userland over `sigqueueinfo`.

## Key Elements
Zeroes a `siginfo_t`, fills signal number, `SI_QUEUE`, caller pid, caller effective uid, and the supplied sigval, then calls `sigqueueinfo`.

## Dependencies
Uses `<signal.h>`, `getpid`, `geteuid`, and `sigqueueinfo`.

## Behavior/Risks
Correct signal provenance depends on filling `si_pid` and `si_uid` from the caller before delegating to the kernel.
