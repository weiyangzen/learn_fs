# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/cmcb.c

This file implements Cache Manager callback routines used by the driver’s `CACHE_MANAGER_CALLBACKS`.

Functions:
- `Ext2AcquireForLazyWrite`: validates the FCB, acquires the file resource exclusive, records the lazy-writer thread, and sets top-level IRP to `FSRTL_CACHE_TOP_LEVEL_IRP`.
- `Ext2ReleaseFromLazyWrite`: verifies/reverses lazy-writer state, releases the file resource, and clears top-level IRP.
- `Ext2AcquireForReadAhead`: acquires the file resource shared for read-ahead and sets top-level IRP.
- `Ext2ReleaseFromReadAhead`: clears top-level IRP and releases the resource.
- `Ext2NoOpAcquire`: for no-op cache callbacks, only sets top-level IRP.
- `Ext2NoOpRelease`: clears top-level IRP.

Research notes:
- These callbacks mediate Cache Manager lazy writer/read-ahead synchronization with the driver’s FCB resources.
- The no-op variants still maintain `IoSetTopLevelIrp` state, which prevents recursive filesystem entry from being misclassified.
