# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_scandisk.c

Disk scanner used to map configured heartbeat region UUIDs to block devices.

It scans devices through `tools-internal/scandisk`, filters to top-level disk devices with usable `/dev` paths, accepts mapper, EMC power, SCSI, loop, Xen, virtio, rbd, drbd, and nbd path prefixes, opens candidate OCFS2 devices with heartbeat-device allowance, fills heartbeat and cluster descriptors, and marks matching `o2cb_device` entries as found.

It retries after short sleeps when sysfs has devices without `/dev` paths. The scanner duplicates region descriptor strings but the file contains a TODO about freeing that allocation, so descriptor ownership is not fully clean.
