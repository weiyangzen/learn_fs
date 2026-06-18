# File Research: sources/local-fs/mtd-utils/include/mtd/inftl-user.h

## Purpose
Userspace definitions for INFTL DiskOnChip metadata.

## Key Elements
Defines OSAK/PERCENT constants, sector size, INFTL OOB block-control/unit-control structures, partition records, media header, and partition flags `INFTL_BINARY`, `INFTL_BDTL`, `INFTL_LAST`.

## Dependencies
Uses Linux integer typedefs such as `__u32` supplied by included system headers in callers.

## Behavior/Risks
On-flash structs are packed and legacy-specific. `docfdisk` relies on these layouts directly.
