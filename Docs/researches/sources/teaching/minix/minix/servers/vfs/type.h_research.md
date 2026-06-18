# File Research: sources/teaching/minix/minix/servers/vfs/type.h

## Purpose
Defines shared VFS support data types for file-server communication, cached mount statistics, service mapping, and socket IDs.

## Main Types
- `comm_t`: per-file-server request throttling state, including max/current outstanding requests and queued workers.
- `struct statvfs_cache`: compact cached subset of `struct statvfs`.
- `struct smap`: service map entry for driver endpoints and labels, with select bookkeeping.
- `sockid_t`: signed 32-bit socket identifier.

## Dependencies
Uses MINIX and system scalar types such as `endpoint_t`, `fsblkcnt_t`, `fsfilcnt_t`, `uint64_t`, and `LABEL_MAX`.

## Risks and Notes
The statvfs cache intentionally avoids embedding full `struct statvfs` to save memory per mount entry. The cache is populated by `update_statvfs()` in `stadir.c`.
