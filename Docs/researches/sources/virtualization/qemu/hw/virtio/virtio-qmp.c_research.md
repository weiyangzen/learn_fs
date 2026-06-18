# File Research: sources/virtualization/qemu/hw/virtio/virtio-qmp.c

## Purpose
Implements QMP helper and query functions for introspecting virtio devices, virtio status bits, virtio/vhost feature bitmaps, and vhost queue state.

## Main Responsibilities
- Provides static feature-description maps for virtio transport features, vhost-user protocol features, virtio config status bits, and many device-specific feature sets.
- Converts feature/status/protocol bitmaps into QAPI linked lists of descriptive strings, preserving unknown residual bits.
- Implements `qmp_x_query_virtio()` by recursively walking the QOM tree and collecting realized `TYPE_VIRTIO_DEVICE` instances.
- Implements `qmp_find_virtio_device()` to resolve a canonical QOM path to a realized `VirtIODevice`.
- Implements `qmp_x_query_virtio_status()` to report virtio device identity, feature sets, endian mode, queue count, status, ISR, selected queue, run/broken/disabled flags, bus name, notifier mask usage, and optional vhost state.
- Implements `qmp_x_query_virtio_vhost_queue_status()` to report one vhost virtqueue’s kick/call fds, descriptor/avail/used virtual pointers, physical addresses, sizes, and queue length.

## Feature Maps Covered
- Transport/ring: notify-on-empty, any-layout, version 1, IOMMU platform, packed ring, in-order, order-platform, SR-IOV, ring reset, indirect desc, event idx.
- Vhost-user protocol: multiqueue, log shmfd, RARP, reply ack, MTU, backend requests, cross-endian, crypto session, pagefault, config, fd passing, host notifier, inflight shmfd, reset, in-band notifications, mem slot configuration, status, shared object, device state.
- Device-specific maps include block, serial, GPU, input, net, SCSI, fs, i2c, vsock, balloon, crypto, IOMMU, mem, rng, and GPIO.
- Devices with no mapped features include 9P, PMEM, IOMEM, RPMSG, clock, WLAN/HWSIM, rproc serial, legacy memory balloon, CAIF, signal distribution, pstore, sound, Bluetooth, RPMB, video encoder/decoder, SCMI, Nitro secure module, watchdog, CAN, DMABUF, parameter service, and audio policy.

## Important Algorithms
- `CONVERT_FEATURES` scans a simple bitmap map, appends matched descriptions, clears matched bits, and leaves unknown bits in the local bitmap.
- `CONVERT_FEATURES_EX` does the same for extended virtio feature arrays using `virtio_has_feature_ex()` and `virtio_clear_feature_ex()`.
- `qmp_decode_features()` copies the source feature array, first strips known transport features, then strips device-specific features based on `device_id`, and finally reports remaining bits as unknown device features.

## Integration Points
- Uses QAPI types from `qapi/qapi-types-virtio.h` and QMP command declarations.
- Uses QOM traversal and object path resolution.
- When a device has vhost started, calls the virtio device class `get_vhost()` method and decodes vhost feature/protocol state.

## Filesystem/Storage Relevance
This is diagnostic and operational infrastructure for virtio storage-like devices, including virtio-blk, virtio-scsi, virtio-fs, and virtio-pmem. It helps inspect negotiated features and vhost queue state during debugging, migration analysis, and performance triage.

## Notable Constraints and Risks
- Unknown feature reporting depends on QAPI fields available for the first two 64-bit words, while the copied feature array can be larger.
- Several feature descriptions are manually maintained strings; typos or stale descriptions can mislead operators without affecting device behavior.
- `qmp_decode_features()` asserts unreachable on unknown virtio device IDs, so new IDs must be added here or explicitly listed as having no features.
