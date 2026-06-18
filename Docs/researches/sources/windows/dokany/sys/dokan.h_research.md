# File Research: sources/windows/dokany/sys/dokan.h

## Role

Primary internal kernel header for the Dokan filesystem driver. It defines global constants, allocation helpers, core device/volume/file/open structures, lock macros, request context structures, function declarations, and flag helpers.

## Major Definitions

- Device names:
  - global Dokan control device
  - filesystem disk/CD device names
  - redirector device names
  - disk symbolic link prefixes
- Allocation:
  - pool tag `TAG`
  - `DokanAlloc`
  - `DokanAllocZero`
  - lookaside list declarations
- Timeouts:
  - pending IRP timeout
  - timeout reset maximum
  - check interval
- Identifier types:
  - `DGL`
  - `DCB`
  - `VCB`
  - `FCB`
  - `CCB`
  - `FREED_FCB`

## Core Structures

- `DOKAN_GLOBAL`:
  - Global driver/device state.
  - Mount list and mount-manager lock.
  - Global filesystem device objects.
- `DokanDCB`:
  - Per mounted disk/device state.
  - Pending IRP queues, notify queue, retry queue.
  - Device names, mount point, UNC name, volume label.
  - Threads, events, mount options, batching and logging options.
- `DOKAN_CONTROL` and `MOUNT_ENTRY`:
  - User-visible mount control and global mount-list entry.
- `DokanVCB`:
  - Per volume state.
  - FCB AVL table, notify list, allocation counters, volume flags, keepalive state, FCB garbage collection, volume metrics.
- `DokanFCB`:
  - Per file/directory control block.
  - Advanced FCB header, section pointers, paging resource, CCB list, open counts, flags, share access, filename, file locks, oplock state, debug state, keepalive/block-dispatch markers.
- `DokanCCB`:
  - Per open context.
  - FCB pointer, user context, search pattern, flags, mount ID, keepalive state, atomic oplock pending state, creating process ID.
- `REQUEST_CONTEXT`:
  - Stable per-IRP snapshot containing device, IRP, stack location, DCB/VCB/global pointers, flags, process ID, and completion/logging state.
- `IRP_ENTRY`:
  - Pending IRP queue node.
- `DEVICE_ENTRY` and `DRIVER_EVENT_CONTEXT`:
  - Device deletion/session and driver-log/event queue helpers.
- `SYMLINK_ECP_CONTEXT`:
  - Undocumented ECP structure used for reparse mount-point filename case repair.

## Locking Interface

Defines debug-aware macros:

- `DokanFCBLockRW`
- `DokanFCBLockRO`
- `DokanFCBUnlock`
- `DokanPagingIoLockRW`
- `DokanPagingIoLockRO`
- `DokanPagingIoUnlock`
- `DokanVCBLockRW`
- `DokanVCBLockRO`
- `DokanVCBUnlock`
- `DokanVCBTryLockRW`

When lock debugging is enabled, macros call `DokanResourceLockWithDebugInfo` and track call sites and owner threads.

## Oplock Support

- Declares dynamic routine pointers:
  - `DokanFsRtlCheckLockForOplockRequest`
  - `DokanFsRtlAreThereWaitingFileLocks`
- Defines `DokanGetFcbOplock` compatibility macro for Win8 and older.
- Defines `DokanOplockDebugInfo` and `DOKAN_OPLOCK_DEBUG_*` flags.
- Declares `DokanCheckOplock`, `DokanOplockRequest`, and debug record helpers.

## Function Declarations

The header declares driver-wide functions for:

- IRP dispatch and completion.
- Create/cleanup/close/read/write/query/set/flush/directory/security/lock handlers.
- Event and pending IRP management.
- Device creation/deletion and mount point operations.
- Reparse point FSCTL payload helpers.
- UNC provider registration.
- MDL allocation/freeing.
- FCB flushing, CCB allocation/freeing, mount lookup, unmount, session cleanup.
- Notification reporting and cleanup.
- Oplock tracking.

## Flag Helpers

Provides atomic flag helpers:

- `DokanSetFlag`
- `DokanClearFlag`
- FCB flag access macros.
- CCB flag aliases over FCB-style flag helpers.
- `DokanFCBIsPendingDeletion`.

## Dependencies

- Windows kernel headers:
  - `ntifs.h`
  - `ntdddisk.h`
  - `ntstrsafe.h`
- Dokan public contract:
  - `public.h`
- Logging:
  - `util/log.h`

## Notes and Risks

- This header defines most cross-file contracts; changes here affect the whole driver.
- Several structure fields include explicit locking comments, but some are marked FIXME.
- CCB flag macros alias FCB flag macros, relying on both structures having a compatible `Flags` field.
- Static SDDL grants broad access to system, administrators, world, and restricted code with different permissions.
