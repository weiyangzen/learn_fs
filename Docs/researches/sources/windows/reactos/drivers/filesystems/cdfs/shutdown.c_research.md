# File Research: sources/windows/reactos/drivers/filesystems/cdfs/shutdown.c

Implements filesystem shutdown handling for CDFS.

Key entry points:
- `CdCommonShutdown()` marks global shutdown, walks all mounted VCBs, purges each active mounted volume, sends `IRP_MJ_SHUTDOWN` to each target device stack, marks the VCB shut down, and attempts dismount.

Core mechanics:
- Popups are disabled during shutdown.
- The global CDFS data resource is acquired while walking `CdData.VcbQueue`.
- Already-shut-down or non-mounted volumes are skipped.
- A fresh synchronous shutdown IRP is built for each target stack because stack sizes can differ.
- After volume processing, the filesystem device object is unregistered and deleted; ReactOS also unregisters/deletes the HDD filesystem device object.

Important invariants:
- The next VCB list link is captured before processing because the current VCB can be deleted during dismount.
- Shutdown should only process each mounted VCB once.
- `CdCheckForDismount()` decides whether the VCB remains and whether its resource must be released.

Filesystem relevance:
- Coordinates final cache purge and lower-device shutdown during system shutdown.

Notable risks:
- The file system device objects are deleted at the end of shutdown; subsequent dispatch must not target them.
- Any failure to allocate a per-stack shutdown IRP is silently skipped for that volume stack.
