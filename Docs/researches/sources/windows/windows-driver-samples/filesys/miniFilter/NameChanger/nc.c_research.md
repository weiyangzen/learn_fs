# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nc.c

This is the main NameChanger minifilter module. It registers the filter, operation callbacks, context types, and name-provider callbacks, and it owns instance attach validation plus global unload cleanup.

Key responsibilities:
- Defines `Callbacks[]` for create, cleanup, query/set information, directory control, network query open, and filesystem control.
- Defines `contextRegistration[]` for `FLT_INSTANCE_CONTEXT` and `FLT_STREAMHANDLE_CONTEXT`.
- Defines `FilterRegistration`, wiring unload, instance setup/teardown, generated name, and name normalization callbacks.
- Owns global driver state through `NC_GLOBAL_DATA NcGlobalData`.

`DriverEntry` initializes compatibility shims with `NcCompatInit`, loads mapping configuration with `NcInitializeMapping`, registers with Filter Manager, then starts filtering. On failed start it unregisters the filter.

`NcInstanceSetup` is the central attach gate. It refuses ReFS because the sample does not handle ReFS V3 USN records, refuses automatic attachment, and requires initialized registry mapping strings. It builds per-volume user and real mapping paths, verifies the user mapping final component does not already exist in either short or long form, verifies the real mapping parent exists, allocates an instance context, builds normalized/short mapping state with `NcBuildMapping`, rejects overlapping real/user mappings, records filesystem type, and stores the context on the instance.

Create/query/set/directory/fsctl callbacks in this file mostly dispatch into feature-specific modules:
- Create path: `NcPreCreate` in `nccreate.c`.
- Directory enumeration and notifications: `NcEnumerateDirectory`, `NcPreNotifyDirectory`, `NcPostNotifyDirectory`.
- File information name fixups: `NcPreQueryAlternateName`, `NcPostQueryName`, `NcPostQueryHardLinks`, rename/link/disposition/short-name handlers.
- FSCTL name fixups: USN, find-by-SID, stream lookup, read journal handlers.
- Name provider: `NcGenerateFileName`, `NcNormalizeNameComponentEx`.

Cleanup handling is synchronized so post-cleanup can safely tear down per-handle notification state through `NcStreamHandleContextNotCleanup`.

`NcPreNetworkQueryCallback` disallows fast I/O for network query opens; the TODO notes these should eventually flow through create-like processing.

Important dependencies:
- `nc.h` for all shared structures and declarations.
- `nccompat.c` for runtime-selected kernel/FltMgr APIs.
- `ncmapping.c`, `ncpath.c`, `ncinit.c`, `ncnameprov.c`, `ncfileinfo.c`, `ncfsctrl.c`, `ncdirenum.c`, `ncdirnotify.c`.

Notable behavior:
- Real mapping paths are hidden from callers; user mapping paths are virtualized and redirected.
- Instance setup deliberately checks both long and short user final components to avoid collisions.
- Deletes on mapping ancestors are constrained elsewhere, but attach itself documents races with `FILE_DELETE_ON_CLOSE`.
