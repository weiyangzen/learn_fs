# sources/security-integrity/fsverity-utils/common/fsverity_uapi.h

Purpose: This header vendors the userspace ABI definitions for Linux fs-verity ioctls, metadata types, hash algorithms, descriptor structures, and enable/read/measure argument layouts.

Important APIs and types: It defines `FS_IOC_ENABLE_VERITY`, `FS_IOC_MEASURE_VERITY`, `FS_IOC_READ_VERITY_METADATA`, `struct fsverity_enable_arg`, `struct fsverity_digest`, `struct fsverity_descriptor`, `struct fsverity_read_metadata_arg`, and metadata/hash constants.

Control flow and state: There is no executable flow. The persistent contract is binary structure layout shared with the kernel, so field sizes, reserved fields, and little-endian encodings are compatibility-critical.

Dependencies and integration points: Used by CLI commands, `lib/enable.c`, digest computation, metadata dump, and tests. It must track kernel UAPI without breaking older build hosts.

Risks and test signals: ABI drift is the primary risk. Misaligned structures or wrong ioctl numbers break kernel interactions. Signals include compile-time structure availability, ioctl success/failure behavior in integration tests, and digest/descriptor vector agreement with kernel expectations.
