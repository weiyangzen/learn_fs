# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_bswap.h

This header defines endian conversion helpers for NILFS scalar fields. On big-endian machines, `nilfs_rw16`, `nilfs_rw32`, and `nilfs_rw64` call byte-swap routines; on little-endian machines they are identity casts.

Integration points: NILFS on-disk structures are little-endian oriented, so callers use these helpers when reading or writing multi-byte on-disk fields across host endian variants.

Risk is caller discipline: this header only provides primitive scalar conversion. Struct fields must be individually converted at every on-disk boundary; missing a conversion on big-endian systems would silently corrupt interpretation.
