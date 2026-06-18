# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/init.c

## Scope
Implements Ext2 driver startup, optional unload, registry configuration loading, global object allocation, device object registration, dispatch-table setup, fast I/O/cache callbacks, lookaside-list initialization, Linux/JBD compatibility initialization, and NLS setup.

## Key Elements
- Defines global `Ext2Global`, build version/date/time strings, `DriverEntry()`, optional `DriverUnload()`, registry query helpers, and ERESOURCE alignment checks.
- `Ext2RegistryQueryCallback()` parses registry values for writing support, bitmap checking, ext3 force writing, auto mount, codepage, hiding prefix, and hiding suffix.
- `Ext2QueryRegistrySettings()` builds the `Parameters` registry path, enables automount by default, applies registry settings, converts configured wide strings to ANSI/OEM fields, and stores the volumes registry path.
- `DriverEntry()` initializes Linux compatibility support, JBD caches, `Ext2Global`, disk and CD-ROM filesystem device objects, reaper threads, major dispatch functions, fast I/O callbacks, cache-manager callbacks, filter callbacks, performance-stat allocation sizes, lookaside lists, symbolic link, NLS tables, and filesystem registration.
- `DriverUnload()` unregisters global resources, deletes the symbolic link, unloads NLS tables, destroys lookaside lists, dereferences registered devices, unloads JBD caches, destroys Linux compatibility state, and frees `Ext2Global`.

## Dependencies
Depends on Windows driver initialization APIs, ReactOS/NT conditional signatures, Ext2 request builder and fast I/O routines, reaper threads, NLS loader, global pool/lookaside helpers, journal module init/exit macros, and Linux compatibility init/teardown.

## Behavior/Risks
- Error cleanup in `DriverEntry()` frees some global/device/JBD/Linux resources but does not mirror all later startup steps because failures can occur at many points.
- Writing support can be enabled directly or implicitly through ext3 force-writing registry configuration.
- The code sets fast I/O mod-write callbacks twice, which is harmless but redundant.
- `Ext2QueryRegistrySettings()` writes `sHidingPrefix[HIDINGPAT_LEN - 1]` after suffix conversion too, likely intending `sHidingSuffix`.
- Resource alignment is asserted at compile time for global, VCB, FCB, block-device, and group-descriptor locks.
