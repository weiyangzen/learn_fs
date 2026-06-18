# File Research: sources/os/bsd/netbsd-src/sys/sys/pipe.h

## Purpose
Defines pipe buffer sizing, pipe state bits, per-pipe kernel structure, and pipe sysctl/init declarations.

## Main API
- Size constants: `PIPE_SIZE`, `BIG_PIPE_SIZE`, `PIPE_DIRECT_CHUNK`, `PIPE_MINDIRECT`.
- Structures: `struct pipebuf`, `struct pipe`.
- State bits: `PIPE_ASYNC`, `PIPE_EOF`, `PIPE_SIGNALR`, `PIPE_LOCKFL`, `PIPE_RESTART`.
- Sysctl subtypes: `KERN_PIPE_MAXKVASZ`, `KERN_PIPE_LIMITKVA`, `KERN_PIPE_MAXBIGPIPES`, `KERN_PIPE_NBIGPIPES`, `KERN_PIPE_KVASIZE`.
- Kernel functions: `sysctl_dopipe`, `pipe_init`.

## Dependencies
Includes select state, time, and UVM declarations.

## Risks and Notes
The header documents direct-write and buffering thresholds. Each pipe has a peer pointer and preallocated KVA buffer, so close/rundown paths must coordinate state, waiters, and peer lifetime carefully.
