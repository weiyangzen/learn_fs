# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/Makefile.inc

Build include fragment for x86_64 libc compatibility.

It includes `gen/Makefile.inc`, and includes `sys/Makefile.inc` only when `${RUMPRUN} != "yes"`.

This conditional avoids pulling syscall compatibility assembly into rump-run builds.
