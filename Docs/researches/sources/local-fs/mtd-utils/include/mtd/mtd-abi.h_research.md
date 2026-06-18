# File Research: sources/local-fs/mtd-utils/include/mtd/mtd-abi.h

## Purpose
User-space MTD ioctl ABI definitions.

## Key Elements
Defines erase, OOB, write-request, MTD info, region info, OTP info, legacy NAND OOB/ECC layout, ECC stats, device type/capability constants, OTP modes, operation modes, ioctl numbers, file modes, and `mtd_type_is_nand_user`.

## Dependencies
Includes `linux/types.h` and relies on ioctl macros from system headers included by users.

## Behavior/Risks
This is ABI surface shared with the kernel. Several interfaces are explicitly obsolete but retained for compatibility, such as `MEMGETOOBSEL` and `nand_ecclayout_user`.
