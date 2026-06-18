# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpfiber.h

## Summary
Internal declarations for the fiber rumpuser scheduler.

## Key Details
- Defines `struct thread` with name, LWP pointer, cookie, wakeup time, TAILQ link, `ucontext_t`, flags, and thread-local errno.
- Defines scheduler/thread flags: runnable, must-join, joined, external stack, and timed out.
- Sets default fiber stack size to 65536 bytes.
- Declares scheduler, wake/block, main-thread initialization, thread exit, scheduler hook, absolute realtime sleep, thread creation, and runnable-flag helpers.

## Notes
This header exposes enough internals for fiber BIO and service-provider support to share the cooperative scheduler.
