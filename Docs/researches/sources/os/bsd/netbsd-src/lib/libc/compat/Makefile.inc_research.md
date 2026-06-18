# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/Makefile.inc

## Scope

Main compatibility build fragment included by libc builds.

## Behavior

- Adds the kernel source include path for compatibility headers.
- Defines `COMPATARCHDIR`.
- Adds architecture-specific gen/sys paths.
- Includes compatibility fragments for db, locale, gen, net, rpc, stdio, stdlib, sys, time, and the selected architecture.

## Dependencies And Invariants

- The selected architecture fragment is loaded through `${COMPATARCHDIR}/Makefile.inc`.
