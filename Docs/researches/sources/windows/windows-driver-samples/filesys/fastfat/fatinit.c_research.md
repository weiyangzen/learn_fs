# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatinit.c

This file implements FastFAT driver initialization, unload cleanup, and two registry-query helpers for compatibility behavior and Fujitsu FMR hardware detection.

Key routines:
- `DriverEntry`
  - Creates the disk filesystem device object named `\Fat`.
  - Creates the CD-ROM filesystem device object named `\FatCdrom`.
  - Installs unload, major IRP dispatch routines, and fast I/O dispatch routines.
  - Registers filesystem filter callbacks, specifically pre-acquire handling for section synchronization.
  - Zeroes and initializes `FatData`.
  - Initializes VCB queues, close lists, close work item, zero page, spin lock, cache-manager callbacks, process pointer, and processor count.
  - Reads `Win31FileSystem` to decide Chicago compatibility behavior.
  - Reads `FatDisableCodePageInvariance` to decide code-page invariance behavior.
  - Initializes the global resource and nonpaged lookaside lists.
  - Initializes close queue synchronization and paging reserve event.
  - Registers both filesystem device objects with the I/O manager and references them.
  - Detects Fujitsu FMR hardware.
  - On Windows 8+ caches global disk accounting state.
- `FatUnload`
  - Deletes lookaside lists and the global resource.
  - Frees the close work item.
  - Dereferences the disk and CD-ROM filesystem device objects.
- `FatGetCompatibilityModeValue`
  - Opens `\Registry\Machine\System\CurrentControlSet\Control\FileSystem`.
  - Queries a named DWORD-like value using `ZwQueryValueKey`.
  - Uses a stack buffer first and allocates a larger paged buffer on overflow.
  - Returns success only when data exists.
- `FatIsFujitsuFMR`
  - Opens `\Registry\Machine\Hardware\DESCRIPTION\System`.
  - Reads `Identifier`.
  - Returns true when it starts with `FUJITSU FMR-`.

Important initialization wiring:
- Major functions are assigned for create, close, read, write, query/set information, query/set EA, flush, query/set volume information, cleanup, directory control, filesystem control, lock control, device control, shutdown, and PNP.
- Fast I/O entries include check-if-possible, copy read/write, basic/standard/network open info, lock/unlock, cache flush acquire/release, and MDL read/write helpers.
- Cache-manager callbacks are configured for lazy write/read-ahead plus no-op variants.
- Delayed close depth scales with `MmQuerySystemSize`.

Failure handling:
- If CD-ROM device creation fails, the disk device is deleted.
- If filter callback registration fails, both device objects are deleted.
- If close work item or zero page allocation fails, created device objects are deleted.
- Registry-query helper frees any allocated query buffer before returning.

Role in the subset:
- This is the FastFAT driver bootstrap file. It connects the filesystem implementation to the Windows I/O manager, cache manager, filter manager callback path, global state, registry configuration, and unload lifecycle.
