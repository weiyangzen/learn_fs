# File Research: sources/os/bsd/netbsd-src/sys/sys/flashio.h

Read completely: 118 lines.

## Purpose
Defines user/kernel ioctl ABI for flash memory devices.

## Main Interfaces
- Status/type enums: `FLASH_ERASE_DONE`, `FLASH_ERASE_FAILED`, `FLASH_TYPE_UNKNOWN`, `FLASH_TYPE_NOR`, `FLASH_TYPE_NAND`.
- Types: `flash_off_t`, `flash_size_t`, `flash_addr_t`.
- Ioctl payloads: `flash_erase_params`, `flash_badblock_params`, `flash_info_params`, `flash_dump_params`.
- Commands: `FLASH_ERASE_BLOCK`, `FLASH_DUMP`, `FLASH_GET_INFO`, `FLASH_BLOCK_ISBAD`, `FLASH_BLOCK_MARKBAD`.

## Dependencies And Integration
Uses `sys/ioctl.h`; includes kernel/standalone or user integer/boolean types depending on context.

## Risks And Edge Cases
- `flash_dump_params` carries a user buffer pointer across ioctl ABI.
- Bad-block state is meaningful mainly for NAND-like media.
- Offset/size types are fixed-width for ABI stability.

## Filesystem Relevance
Moderate. Supports flash media operations underneath flash filesystems or block abstractions.
