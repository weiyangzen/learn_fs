# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpr.h

## Role

Defines common checkpoint/resume, suspend-to-disk, reusable statefile, CPR boot, and suspend-to-RAM constants and structures.

## Public/Common Configuration

- `CPR_VERSION`, `CPR_CONFIG`: CPR config version and config path.
- `CPR_CONFIG_MAGIC`, `CPR_DEFAULT_MAGIC`: file magic values.
- `cpr_prop_info`, `cpr_default_mini`, `cpr_default_info`: NVRAM/default CPR metadata.
- `struct cprconfig`: pmconfig-provided statefile and power-management configuration.
- `CFT_UFS`, `CFT_SPEC`, `CFT_ZVOL`: statefile placement types.

## Kernel Statefile Format

Under `_KERNEL`, the file defines the on-disk/on-statefile CPR format:

- `cpr_dump_desc`: dump header.
- `cpr_bitmap_desc`: physical memory bitmap descriptor.
- `cpr_storage_desc`: storage description for dirty/clean pages.
- `cpr_page_desc`: page record descriptor, including compression/checksum flags.
- `cpr_machdep_desc`: machine-dependent resume block descriptor.
- `cpr_terminator`: end marker with statefile size and timing data.
- Magic constants: `CPR_DUMP_MAGIC`, `CPR_BITMAP_MAGIC`, `CPR_PAGE_MAGIC`, `CPR_MACHDEP_MAGIC`, `CPR_TERM_MAGIC`.

## CPR Control Constants

- `AD_CPR_*`: uadmin subcommands for compression, reusable CPR, test modes, debug modes, printing stats, suspend-devices-only, and no-compress flows.
- `AD_LOOPBACK_SUSPEND_TO_RAM_*`, `AD_FORCE_SUSPEND_TO_RAM`, `AD_DEVICE_SUSPEND_TO_RAM`: suspend-to-RAM testing/development commands.
- `DEV_SUSPEND_TO_RAM`, `DEV_CHECK_SUSPEND_TO_RAM`: temporary non-ON application compatibility commands.
- `CPR_DEFAULT`, `CPR_STATE_FILE`: hardcoded cprboot-related paths.
- `CPR_SPEC_OFFSET`: offset used when CPR statefile I/O targets a block device.

## Kernel Runtime State

- `cpr_t`: central CPR state, including flags, substate, active vnode, bitmap descriptors, reserved mapping area, statistics, and allocation retry count.
- Global access macros: `CPR`, `STAT`, `C_VP`.
- Flags: `C_SUSPENDING`, `C_RESUMING`, `C_COMPRESSING`, `C_REUSABLE`, `C_ERROR`.
- Substates: from `C_ST_SUSPEND_BEGIN` through CPU offline, thread stopping, statefile allocation, device suspension, dump, reusable, nodump, and MP paused phases.
- `DCF_CPR_SUSPENDED`: device flag indicating CPR suspend occurred.
- `CPR_TORAM`, `CPR_TODISK`: suspend target differentiation.

## Function Surface

Declares many CPR kernel routines for:

- Statefile path construction and PROM path/property handling.
- Default CPR setup, validation, and file I/O.
- Dumping, reading dump headers, physical pages, terminators, and machine-dependent blocks.
- Device suspend/resume.
- CPU offline/online, CPU allocation/freeing, and CPU stop handling.
- User/kernel thread stop/start/signal handling.
- Bitmap allocation, cleanup, page counting, and page range display.
- Statistics collection, event timing, and reporting.
- Time-of-day save/restore/status.
- Error reporting via `cpr_err()`.

## Important Constraints

- Comments explicitly state CPR statefile structures must remain layout-compatible between ILP32 and LP64 kernels because `cprboot` supports both.
- Bitmap and page descriptors encode physical memory state; layout stability matters for resume correctness.
- `PROM_MAX_READ`, `CPR_MAX_BLOCK`, and `CPR_MAXCONTIG` constrain I/O chunking.

## Research Relevance

This is central to illumos suspend/resume and statefile handling. It intersects filesystem research through statefile placement on UFS, special devices, and ZVOLs, plus direct vnode/block-device I/O during kernel checkpoint.
