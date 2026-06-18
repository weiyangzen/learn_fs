# File Research: sources/os/bsd/freebsd-src/sys/kern/Makefile

## Summary
Small makefile wrapper for generating kernel syscall tables and related headers.

## Main Contents
Defines `GENERATED` outputs: `init_sysent.c`, `syscalls.c`, `systrace_args.c`, and generated syscall headers/make fragments under `${SYSDIR}/sys`.

## Important Behavior
Includes `../conf/sysent.mk`, which contains the actual syscall generation rules.

## Risks
This file is declarative. Incorrect `GENERATED` entries would affect cleanup or dependency tracking for syscall-generation artifacts.
