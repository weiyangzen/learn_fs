# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_checksum.h

This header defines the generic 256-bit ZFS checksum value and basic checksum macros.

Core definitions:
- `zio_cksum_t` contains four 64-bit words.
- `ZIO_SET_CHECKSUM()` assigns all four words.
- `ZIO_CHECKSUM_EQUAL()` compares checksums by OR-ing word deltas.
- `ZIO_CHECKSUM_IS_ZERO()` tests for an all-zero checksum.
- `ZIO_CHECKSUM_BSWAP()` byte-swaps each checksum word in place.

Risk-sensitive invariants:
- This type is embedded in `blkptr_t` and is part of on-disk metadata.
- Byte swapping must be applied per 64-bit word, not to the structure as arbitrary bytes.
