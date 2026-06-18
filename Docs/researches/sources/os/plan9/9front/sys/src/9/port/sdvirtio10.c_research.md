# File Research: sources/os/plan9/9front/sys/src/9/port/sdvirtio10.c

Plan 9 `SDifc` driver for non-legacy Virtio 1.0 block and SCSI devices.

Key responsibilities:
- Discovers Virtio PCI devices with modern IDs for block and SCSI device types.
- Parses Virtio PCI capability structures and maps common, notify, ISR, and device-specific config regions.
- Resets devices, acknowledges driver status, negotiates minimal feature bits, allocates virtqueues, and publishes descriptor/avail/used rings.
- Implements vring descriptor allocation, completion processing, wakeup, and notify writes.
- Implements virtio-blk request submission, including read, write, and flush-like request handling.
- Implements virtio-scsi command submission with CDB, response, sense, data, and residual handling.
- Presents virtio-blk and virtio-scsi devices through the Plan 9 `sd` interface.
- Delegates virtio-scsi online/verify/bio paths to the shared SCSI helpers.

Dependencies:
- Uses `virtio10.h` accessors and `Vio` mapped-register abstraction.
- Uses PCI discovery/config helpers and Plan 9 `sd` plus SCSI helper routines.
- Uses `PADDR`, `coherence`, interrupts, and kernel rendezvous sleep.

Notable behavior:
- The driver exists specifically for modern virtio devices where legacy I/O-port transport is disabled.
- Block devices are assigned IDs from `'F'`; virtio-scsi devices from `'0'`.
- For virtio-scsi, queue 2 is used for command traffic.
- Completion paths free descriptor chains and clear per-request `rock` records.
