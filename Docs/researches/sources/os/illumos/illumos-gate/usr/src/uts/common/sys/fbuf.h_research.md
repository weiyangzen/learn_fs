# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fbuf.h

## Role

`fbuf.h` defines the kernel `fbuf` interface for mapping a region of a vnode-backed file through segkmap/segmap-style facilities.

## API

- `struct fbuf` contains mapped address and byte count.
- `fbread()` maps file data for read/write-style access.
- `fbzero()` maps/zeros file data.
- `fbwrite()` synchronously writes a mapped buffer using file mapping information.
- `fbdwrite()` performs delayed write handling.
- `fbiwrite()` synchronously writes indirectly to a specified block number without using file mapping information.
- `fbrelse()` releases a mapped `fbuf` with a `seg_rw` release code.

## Filesystem Relevance

Filesystem code can use this interface to access directory blocks or metadata through kernel mappings while retaining explicit control over release/writeback behavior.
