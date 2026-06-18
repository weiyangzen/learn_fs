# File Research: sources/windows/dokany/sys/public.h

Defines Dokan's public kernel/user ABI: IOCTL/FSCTL codes, driver version, event context structures, event reply structures, mount/start flags, driver-info flags, mount-point info, and special names.

Key contents:
- Version and limits: `DOKAN_DRIVER_VERSION`, `EVENT_CONTEXT_MAX_SIZE`, `VOLUME_SECURITY_DESCRIPTOR_MAX_SIZE`, default sector/allocation/disk sizes, default event-info buffer sizes.
- FSCTL codes: version/debug, event start/release/write/process-and-pull, timeout reset, access token, mount-point list/cleanup, keepalive activation, path notification, volume metrics.
- File/CCB/FCB flags: directory, deleted/opened, delete-on-close, paging/synchronous/nocache, retry create, notify-list use, last-write change, delete-pending.
- Mount device types: disk filesystem and network filesystem.
- Special FCB names: keepalive and notification files.
- Intermediate structures for variable strings, notify path, access state, IO security context, and create security payloads.
- Operation payload structs: create, cleanup, close, directory, read, write, file info, set file, volume, lock, flush, unmount, query security, set security.
- `EVENT_CONTEXT`: variable-length kernel-to-user request envelope with common fields and operation union.
- `EVENT_INFORMATION`: user-to-kernel reply envelope with serial number, status, operation-specific result union, context, buffer length, pull timeout, and inline buffer.
- `VOLUME_METRICS`: counters for FCB garbage collection, allocations/deletions, cancellations, and oversized IRP registration cancellation.
- Mount options: alternate streams, write-protect, removable, mount manager, current session, user-mode file locks, case-sensitive, network unmount, driver log dispatch, IPC batching, drive-letter-in-use.
- `EVENT_DRIVER_INFO` and mount result flags describing forced mount, auto-assign request, old-drive replacement, no mount point, and reparse-point failure.
- `EVENT_START`: user-mode mount request, including device type, flags, mount point, UNC name, timeout, FCB GC interval, and optional volume security descriptor.
- `DOKAN_RENAME_INFORMATION`: architecture-neutral rename payload.
- `DOKAN_MOUNT_POINT_INFO`: mount-list record returned to callers.
- `DOKAN_LOG_MESSAGE`: driver log message payload dispatched through the event mechanism.

Core mechanics:
- The ABI uses fixed headers plus trailing variable arrays to marshal file names, security descriptors, read/write buffers, search patterns, and rename targets.
- Several intermediate structures replace kernel pointer-rich types with offsets for safe cross-boundary copying.
- `WRITE_MAX_SIZE` reserves room for `EVENT_CONTEXT` and a conservative filename allowance inside the maximum event context size.
- `DOKAN_EVENT_INFO_DEFAULT_SIZE` pools page-sized reply buffers for common read/write replies.

Filesystem relevance:
- This header is the contract between the Dokan kernel driver and user-mode filesystem library. Any layout or flag change affects IPC compatibility.

Notable risks:
- Structure packing, pointer-size differences, and offset alignment are central ABI concerns, especially rename and security payloads.
- Fixed-size mount/UNC/device arrays constrain path lengths.
- Driver/user version mismatch is explicitly checked at mount start.
