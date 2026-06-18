# File Research: sources/os/bsd/netbsd-src/sys/sys/filio.h

Read completely: 64 lines.

## Purpose
Defines generic file-descriptor ioctls.

## Main Interfaces
- Close-on-exec ioctls: `FIOCLEX`, `FIONCLEX`.
- Hole/data seeking ioctls: `FIOSEEKDATA`, `FIOSEEKHOLE`.
- Readiness/queue ioctls: `FIONREAD`, `FIONWRITE`, `FIONSPACE`.
- Nonblocking/async/owner ioctls: `FIONBIO`, `FIOASYNC`, `FIOSETOWN`, `FIOGETOWN`.
- Block mapping: `OFIOGETBMAP`, `FIOGETBMAP`, alias `FIBMAP`.

## Dependencies And Integration
Uses ioctl command encoding and `off_t`/`daddr_t`. Vnode fileops and device/socket code implement relevant commands.

## Risks And Edge Cases
- `OFIOGETBMAP` preserves old 32-bit block-number ABI.
- `FIOSEEKDATA`/`FIOSEEKHOLE` rely on filesystem support for sparse file knowledge.

## Filesystem Relevance
High. Provides generic file ioctls, including hole/data and block mapping queries.
