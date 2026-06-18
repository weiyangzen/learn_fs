# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_checksum.h

Defines checksum function signatures, checksum metadata flags, ABD checksum iteration hooks, checksum info table entries, bad-checksum reports, and checksum compute/verify APIs.

Key elements:
- `zio_checksum_t` computes a checksum over an ABD.
- Template init/free hooks support salted algorithms.
- Flags identify metadata-safe, embedded, dedup-safe, salted, and nopwrite-safe checksums.
- `zio_abd_checksum_func_t` provides init/fini/iter callbacks for ABD checksum traversal.
- `zio_checksum_info_t` records byteorder-specific functions, template hooks, flags, and name.
- `zio_bad_cksum_t` reports expected/actual checksum, algorithm name, byteswap, injection, and validity.

Main dependencies and interactions:
- Depends on `zio.h`, feature mapping, and Fletcher support.
- Declares SHA, Skein, Edon-R, and Fletcher checksum entry points.
- Exposes checksum equality, compute, error, dedup checksum selection, template cleanup, and feature mapping.

Implementation notes:
- Byteorder is explicit through `ZIO_CHECKSUM_NATIVE` and `ZIO_CHECKSUM_BYTESWAP`.
