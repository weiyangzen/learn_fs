# File Research: sources/local-fs/xfsdump/librmt/rmtlseek.c

Implements `rmtlseek(fildes, offset, whence)`.

Behavior:
- Local descriptors call `lseek(2)`.
- Remote descriptors send `L<offset>\n<whence>\n` and return `_rmt_status()`.

Notable detail:
- Serializes `off_t` as `long`, which may truncate on platforms where `off_t` exceeds `long`.
