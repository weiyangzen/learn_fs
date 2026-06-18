# File Research: sources/teaching/minix/minix/drivers/storage/vnd/Makefile

## Purpose

Builds the MINIX vnode disk driver service.

## Build Role

Defines `PROG=vnd` from `vnd.c`, links against `libblockdriver` and `libsys`, and includes `minix.service.mk`.

## Dependencies

Requires blockdriver support and system-call helpers for safe copying and service operation.

## Risks

Simple build file; correctness depends on `vnd.c` receiving blockdriver and system libraries.
