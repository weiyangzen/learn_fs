# File Research: sources/local-fs/squashfs-tools/squashfs-tools/nprocessors_compat.h

Small public header for processor-count compatibility support.

Exports:
- `get_nprocessors(void)`

Role:
- Allows option/default sizing code to query the effective processor count without caring about the platform-specific implementation.

Notes:
- Implementation caches the result in `nprocessors_compat.c`.
