# sources/test-tools/fio/oslib/libmtd_int.h

Purpose: private MTD library internals shared between sysfs and legacy implementations.

Important APIs/types: defines `PROGRAM_NAME`, sysfs path fragment constants, 64-bit ioctl support states, private `struct libmtd`, and legacy fallback prototypes.

Control flow and state: `struct libmtd` holds allocated sysfs path patterns, a `sysfs_supported` bit, and a cached two-bit `offs64_ioctls` state initialized as unknown then updated by runtime ioctl probing.

Dependencies and integration: included by `libmtd.c` and `libmtd_legacy.c`; imports the public types from `libmtd.h` in implementation files.

Risks: private layout is cast from opaque `libmtd_t`, so all implementations must agree. Cached ioctl support is per-library descriptor and not synchronized.

Test signals: sysfs-supported and legacy paths both need coverage, including transition from unknown to supported/not-supported 64-bit ioctl states.
