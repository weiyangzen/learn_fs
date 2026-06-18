# sources/test-tools/strace/bundled/linux/include/uapi/mtd/mtd-abi.h

## Purpose
Defines the primary Linux Memory Technology Device userspace ABI that strace uses to decode MTD ioctl commands and payloads: flash geometry, erase/OOB/read/write requests, ECC statistics, OTP operations, bad-block management, lock state, file modes, and legacy NAND OOB layouts.

## Important APIs, Types, and Functions
Read coverage: 342 lines and 11876 bytes. Core request structures are `erase_info_user`, `erase_info_user64`, `mtd_oob_buf`, `mtd_oob_buf64`, `mtd_write_req`, `mtd_read_req_ecc_stats`, and `mtd_read_req`. Device descriptions use `mtd_info_user`, `region_info_user`, and `otp_info`. Flash type and capability constants include `MTD_RAM`, `MTD_ROM`, `MTD_NORFLASH`, `MTD_NANDFLASH`, `MTD_DATAFLASH`, `MTD_UBIVOLUME`, `MTD_MLCNANDFLASH`, `MTD_WRITEABLE`, `MTD_BIT_WRITEABLE`, `MTD_NO_ERASE`, `MTD_POWERUP_LOCK`, `MTD_SLC_ON_MLC_EMULATION`, and capability bundles. Operation modes include `MTD_OPS_PLACE_OOB`, `MTD_OPS_AUTO_OOB`, and `MTD_OPS_RAW`; file modes include normal, factory/user OTP, and raw.

Ioctl commands include `MEMGETINFO`, `MEMERASE`, `MEMWRITEOOB`, `MEMREADOOB`, `MEMLOCK`, `MEMUNLOCK`, `MEMGETREGIONCOUNT`, `MEMGETREGIONINFO`, `MEMGETOOBSEL`, `MEMGETBADBLOCK`, `MEMSETBADBLOCK`, `OTPSELECT`, `OTPGETREGIONCOUNT`, `OTPGETREGIONINFO`, `OTPLOCK`, `ECCGETLAYOUT`, `ECCGETSTATS`, `MTDFILEMODE`, `MEMERASE64`, `MEMWRITEOOB64`, `MEMREADOOB64`, `MEMISLOCKED`, `MEMWRITE`, `OTPERASE`, and `MEMREAD`. Legacy compatibility structures include `nand_oobinfo`, `nand_oobfree`, `nand_ecclayout_user`, and `mtd_ecc_stats`. The inline helper `mtd_type_is_nand_user` identifies SLC and MLC NAND types.

## Control Flow
Userspace opens an MTD character device, queries geometry with `MEMGETINFO`, optionally discovers erase regions, OOB layout, and ECC stats, then performs erase, read, write, OOB, lock/unlock, OTP, or bad-block operations. Newer generic `MEMREAD` and `MEMWRITE` carry data and OOB userspace addresses plus an operation mode, while older OOB calls use 32-bit or 64-bit OOB buffer descriptors. File mode can be set per descriptor to raw or OTP behavior and affects read/write paths that cannot carry per-operation mode.

## State and Persistence Behavior
The header itself is stateless, but its ioctls mutate persistent flash contents, OOB areas, bad-block tables, OTP regions and locks, erase state, and chip lock state. `mtd_info_user`, `region_info_user`, and ECC structures snapshot kernel device state. File mode is per-open-file-descriptor runtime state. ECC counters and bad-block state are persistent or device-maintained signals that strace can reveal through decoded ioctl payloads.

## Dependencies and Integration Points
Direct include is `<linux/types.h>`. In strace this bundled header integrates with ioctl number tables and structure decoders for MTD tools. Kernel ecosystem integration includes `/dev/mtd*` character devices, NAND/NOR/dataflash drivers, nandsim/mtdram, mtd-utils, UBI attachment, flash filesystems, bootloaders, and manufacturing or recovery tools.

## Risks and Edge Cases
Flash operations can be destructive: erase, raw write, OTP lock, OTP erase, and bad-block marking are high-risk. ABI compatibility risks include legacy 32-bit offsets versus 64-bit offsets, userspace pointers in old structures, only lower 32 bits of `len`/`ooblen` being used in generic requests, reserved padding that must be zero, deprecated OOB/ECC layout truncation, raw mode bypassing ECC, and loff_t compat for bad-block ioctls. Strace decoders must avoid assuming a specific flash geometry and must treat user pointers as addresses.

## Test Signals
Use strace tests for every `MEM*`, `OTP*`, and `ECC*` ioctl name and representative payload formatting, including compat layouts. Behavioral tests can run mtd-utils on nandsim/mtdram, covering query, erase, OOB read/write, generic read/write with ECC stats, raw mode, OTP paths where emulated, bad-block get/set, lock state, and UBI attach after MTD operations.
