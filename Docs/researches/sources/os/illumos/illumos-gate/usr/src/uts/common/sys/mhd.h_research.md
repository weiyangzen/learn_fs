# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mhd.h

Purpose: Defines multi-host device ioctl commands and structures, primarily for SCSI-3 persistent group reservations.

Key definitions:
- Ioctls: failfast, take ownership, release, status, in-keys, in-reservations, register, reserve, preempt/preempt-and-abort, clear, register-and-ignore-key, query reserve, re-register device ID.
- `mhioctkown`: ownership delay parameters.
- Reservation key/list/descriptor/list structures with 32-bit syscall variants.
- Register, preempt-and-abort, and register-and-ignore-key request structures.
- SCSI-3 reservation type and scope codes.

Important detail: 8-byte reservation keys are fixed by `MHIOC_RESV_KEY_SIZE`.

Relevance to subset A: Storage clustering/multi-host reservation ABI, directly relevant to block-storage correctness.
