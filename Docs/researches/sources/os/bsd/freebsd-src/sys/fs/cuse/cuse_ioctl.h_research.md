# File Research: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse_ioctl.h

Read completely: 90 lines.

Purpose: defines CUSE control-device ioctl ABI structures and ioctl numbers for `/dev/cuse`.

Key structures:
- `struct cuse_data_chunk` describes data transfer between local and peer pointers with length.
- `struct cuse_alloc_info` describes mmap shared-memory page allocation by `page_count` and `alloc_nr`.
- `struct cuse_command` is the server-visible command record: device pointer, flags, per-file handle, data pointer, argument, and command code.
- `struct cuse_create_dev` describes user-requested device creation, owner/group/mode, and devnode name.

Key limits:
- `CUSE_BUFFER_MAX` is 4096 bytes.
- `CUSE_DEVICES_MAX` is 64.
- Reserved ioctl-buffer pointer window is `0x10000` to `0x20000`.
- Allocation numbers are limited by `CUSE_ALLOC_UNIT_MAX`; offsets use `CUSE_ALLOC_UNIT_SHIFT`.

Ioctls:
- Defines get command, read/write data, sync command, get signal, allocate/free memory, set per-file handle, create/destroy device, allocate/free units, select wakeup, and ID-based unit allocation/free.

Research notes:
- This is the ABI contract that `cuse.c` implements.
- Pointer fields are `uintptr_t`, supporting cross-process and compat handling.
