# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_impl.h

Defines private ZIO pipeline stage bits and precomposed pipeline masks for read, write, free, claim, ioctl, trim, DDT, gang, and vdev child I/O.

Key elements:
- `enum zio_stage` covers open, BP init, async issue, compression, encryption, checksum generate/verify, nopwrite, DDT read/write/free, gang assemble/issue, DVA throttle/allocate/free/claim, ready, vdev I/O start/done/assess, and done.
- Pipeline masks include interlock, vdev child, read physical, read logical, DDT read, write physical, rewrite, write, DDT child write, DDT write, free, DDT free, claim, ioctl, trim, and blocking stages.
- Declares `zio_inject_init()` and `zio_inject_fini()`.

Main dependencies and interactions:
- Included by `zio.h`.
- Used internally by ZIO executor to advance I/O through staged behavior.

Implementation notes:
- The header comment documents compression, dedup, nopwrite, and encryption transformations.
- Nopwrite is explicitly mutually exclusive with encryption except encrypted dedup has special deterministic handling.
