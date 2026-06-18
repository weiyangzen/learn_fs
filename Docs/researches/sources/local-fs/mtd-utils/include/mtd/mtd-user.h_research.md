# File Research: sources/local-fs/mtd-utils/include/mtd/mtd-user.h

## Purpose
Small compatibility wrapper for userspace MTD ABI inclusion.

## Key Elements
Includes `stdint.h` and `mtd/mtd-abi.h`, then typedefs common old names such as `mtd_info_t`, `erase_info_t`, `region_info_t`, `nand_oobinfo_t`, and `nand_ecclayout_t`.

## Dependencies
Depends on `mtd/mtd-abi.h`.

## Behavior/Risks
Keeps older code compiling against newer ABI struct names.
