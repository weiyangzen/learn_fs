# File Research: sources/os/bsd/freebsd-src/sys/kern/Make.tags.inc

## Summary
Defines common file and directory lists included by architecture-specific kernel `make tags` targets.

## Main Contents
- `SYS ?= ${.CURDIR}/..` defaults the kernel source root.
- `COMM` lists common source globs for ctags, including `sys/vnode.h`, major `dev`, `fs`, `geom`, `kern`, networking, UFS, VM, and `sys` headers/sources.
- `COMMDIR1` and `COMMDIR2` list directories used by tag generation.

## Important Behavior
The file intentionally places `/sys/sys` include files at the end of `COMM` so subroutine definitions win over same-name struct tags, such as `vmmeter`.

## Risks
This is build tooling, not runtime code. The main maintenance risk is stale directory lists causing incomplete kernel tags for developers.
