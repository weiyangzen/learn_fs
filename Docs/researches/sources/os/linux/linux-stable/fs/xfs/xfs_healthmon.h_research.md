# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_healthmon.h

## Purpose

Defines the internal live-health-monitor data structures, event taxonomy, and reporting API used by XFS code to deliver health events to userspace.

## Main Types

- `struct xfs_healthmon`
  - Stores the weak mount cookie, device number, refcount, event queue, wait queue, output buffer, lost-event counters, and verbose-mode flag.
- `enum xfs_healthmon_type`
  - Represents monitor lifecycle, lost events, unmount, shutdown, metadata health changes, media errors, and file-range I/O error events.
- `enum xfs_healthmon_domain`
  - Identifies the affected object class: mount, filesystem metadata, allocation group, inode, realtime group, data/log/realtime device, or file range.
- `struct xfs_healthmon_event`
  - Queue node containing event type/domain/time and a union of event-specific payloads.

## Main API

- `xfs_healthmon_unmount`
- `xfs_healthmon_report_fs`
- `xfs_healthmon_report_group`
- `xfs_healthmon_report_inode`
- `xfs_healthmon_report_shutdown`
- `xfs_healthmon_report_media`
- `xfs_healthmon_report_file_ioerror`
- `xfs_ioc_health_monitor`

## Important Invariants

- The mount pointer is stored only as an opaque cookie and is explicitly documented as unsafe to dereference by generic users.
- The open fd, the mount, and running event handlers each hold references to the monitor object.
- Event list and event counters are protected by `lock`.
- Formatting-buffer cursors are protected by the anonymous file inode lock.
- `unmount_event` is preallocated because unmount notification must not fail due to memory pressure.

## Dependencies

This header depends on XFS mount, inode, group, device, and userspace ioctl structures that are included by implementation files before including this header.

## Research Notes

The header is the narrow internal contract between health state producers and the monitor fd implementation. It also documents the locking model that keeps queue operations independent from the mount lifetime.
