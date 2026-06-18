# File Research: sources/os/bsd/netbsd-src/sys/kern/Makefile

## Purpose
Top-level makefile for generated kernel files and tags-link maintenance under `sys/kern`.

## Main Interfaces
- Generates syscall outputs from `makesyscalls.sh`, `syscalls.conf`, and `syscalls.master`.
- Generates vnode interface files from `vnode_if.sh` and `vnode_if.src`.
- Builds a diagnostic `subr_vmem` helper target.
- `tags` recurses into selected architectures; `links` creates symlinks to the machine tags file.

## Implementation Notes
The default `all` target intentionally fails with guidance to invoke only supported maintenance targets.

## Dependencies
Uses BSD make, `${HOST_SH}`, tool variables, and `<bsd.files.mk>`.
