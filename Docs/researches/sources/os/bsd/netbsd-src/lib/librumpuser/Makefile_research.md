# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/Makefile

Read completely: 61 lines.

## Purpose
Builds `librumpuser`, the userspace support layer used by rump kernels.

## Main Responsibilities
- Disables full RELRO and sets warning level 5 by default.
- Adds the rump include path so `rumpuser.h` can be installed from `sys/rump/include/rump`.
- Selects the implementation source set based on `RUMPUSER_THREADS`: `pthread`, `none`, or `fiber`.
- For pthread mode, depends on `libpthread` and builds `rumpuser.c`, `rumpuser_pth.c`, `rumpuser_bio.c`, and `rumpuser_sp.c`.
- For no-thread mode, builds the dummy pthread implementation.
- For fiber mode, enforces `RUMP_CURLWP=hypercall` if `RUMP_CURLWP` is set, then builds fiber-specific sources.
- Always builds component, random, file, memory, error translation, and signal translation sources.
- Adds optional dynamic-loading and daemonization sources.
- Installs `rumpuser_component.h` and `rumpuser_port.h` under `/usr/include/rump`.
- Defines `LIBRUMPUSER` and `_REENTRANT`.

## Filesystem Relevance
High indirect relevance. `librumpuser` supplies the host-facing services, file/memory helpers, threading, and error/signal translation that rump filesystem kernels need to run in userspace.

## Dependencies
- `bsd.own.mk` and `bsd.lib.mk`.
- Optional `../libpthread`.
- Rump public include files from `sys/rump/include/rump`.
