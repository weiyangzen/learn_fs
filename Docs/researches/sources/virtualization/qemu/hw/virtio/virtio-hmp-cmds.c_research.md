# File Research: sources/virtualization/qemu/hw/virtio/virtio-hmp-cmds.c

Implements human monitor protocol (HMP) commands for inspecting virtio devices by formatting the QAPI `x-query-virtio*` results into monitor text.

Key entry points:
- `hmp_virtio_query()` lists all virtio devices returned by `qmp_x_query_virtio()`, showing QOM path and device name.
- `hmp_virtio_status()` prints device identity, lifecycle flags, queue counts, ISR/endianness, status bits, guest/host/backend feature sets, and optional vhost state.
- `hmp_vhost_queue_status()` prints vhost vring kick/call fds and descriptor/avail/used addresses, physical addresses, and sizes for one queue.
- `hmp_virtio_queue_status()` prints QEMU virtqueue state: queue index, inuse count, used index, notification state, optional last/shadow avail indices, and vring layout.
- `hmp_virtio_queue_element()` prints one queue element, including descriptor address/length/flags plus avail and used entries.

Formatting helpers:
- `hmp_virtio_dump_protocols()` prints known vhost protocol feature names and an optional unknown bitmask.
- `hmp_virtio_dump_status()` prints decoded virtio status names and optional unknown status bits.
- `hmp_virtio_dump_features()` prints transport, device, and unknown feature bitmaps, including the high/low 128-bit unknown-device-feature display.

Core mechanics:
- The file is intentionally presentation-only. It delegates discovery and state extraction to QAPI commands in `qapi/qapi-commands-virtio.h`.
- Each HMP command first calls the corresponding QMP query function, handles `Error`, then prints selected fields with `monitor_printf()`.
- Returned QAPI objects are released with their generated `qapi_free_*()` destructors.
- Optional QAPI fields such as `has_last_avail_idx`, `has_shadow_avail_idx`, `has_unknown_*`, and `vhost_dev` are checked before printing.

Important invariants:
- The HMP `path` and `queue` arguments are passed unchanged to QMP query functions; validation is expected in the QMP/backend query layer.
- Queue element lookup uses `index != -1` as the QAPI "index provided" flag.
- HMP output mirrors QAPI schema fields and has no independent synchronization around virtio state.

Filesystem/block relevance:
- This file is not a data path. It is operational inspection tooling for virtio devices, including queues used by virtio block, virtio-fs-related transports, and other virtual I/O devices.

Notable risks:
- Output can become stale immediately because it snapshots live device state without locking in this HMP layer.
- Formatting depends on QAPI structure stability; schema changes require corresponding HMP updates.
