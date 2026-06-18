# File Research: sources/os/bsd/freebsd-src/sys/sys/filio.h

## Purpose
Defines generic file descriptor ioctls shared by files, devices, sockets, pipes, and some VFS objects.

## Main Interfaces
- Ioctls:
  - `FIOCLEX`, `FIONCLEX`
  - `FIONREAD`, `FIONBIO`, `FIOASYNC`
  - `FIOSETOWN`, `FIOGETOWN`
  - `FIODTYPE`, `FIOGETLBA`
  - `FIODGNAME`
  - `FIONWRITE`, `FIONSPACE`
  - `FIOSEEKDATA`, `FIOSEEKHOLE`
  - `FIOBMAP2`
  - `FIOSSHMLPGCNF`, `FIOGSHMLPGCNF`
- `struct fiodgname_arg`.
- `struct fiobmap2_arg`.
- Kernel 32-bit compatibility `struct fiodgname_arg32`, `FIODGNAME_32`.
- Kernel helper `fiodgname_buf_get_ptr`.

## Dependencies And Integration
Includes `_types.h` and `ioccom.h`. Integrates with VFS sparse-file seeking, block mapping, descriptor flags, and POSIX shm largepage configuration.

## Risk Notes
Ioctl numbers and argument layouts are ABI. `FIODGNAME` needs pointer translation on 32-bit compatibility paths.
