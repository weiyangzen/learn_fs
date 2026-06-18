# File Research: sources/virtualization/qemu/hw/virtio/virtio-mmio.c

Implements the virtio MMIO transport device and bus, including legacy and modern MMIO registers, queue setup, feature negotiation, interrupts, ioeventfd integration, migration state, and sysbus realization.

Key entry points:
- `virtio_mmio_read()` handles guest reads from virtio-mmio registers and device configuration space.
- `virtio_mmio_write()` handles guest writes for feature selection, queue configuration, notifications, interrupt ack, status changes, and config writes.
- `virtio_mmio_realizefn()` creates the virtio-mmio bus, IRQ, and MMIO region in legacy or modern endianness mode.
- `virtio_mmio_update_irq()` drives the sysbus IRQ based on the virtio device ISR.
- `virtio_mmio_reset()` and `virtio_mmio_soft_reset()` reset transport state and virtio bus/device state.
- `virtio_mmio_set_guest_notifiers()` configures event notifiers for virtqueues and config changes.
- `virtio_mmio_bus_class_init()` wires the virtio bus callbacks for notify, migration config, ioeventfd, guest notifiers, pre-plug, VM state changes, and device path.

Register behavior:
- With no backend device, reads return valid magic/version/vendor and zero for most other registers so guest probing sees no device id; writes are ignored.
- Device config space begins at `VIRTIO_MMIO_CONFIG` and uses legacy or modern config accessors depending on `force-legacy`.
- Non-config register accesses must be 32-bit; wrong-size accesses are logged as guest errors.
- Legacy mode supports `QUEUE_PFN`, `QUEUE_ALIGN`, and `GUEST_PAGE_SIZE`.
- Modern mode supports 64-bit split descriptor/avail/used addresses, queue-ready state, config generation, and 64-bit feature negotiation.

Queue and feature mechanics:
- `DEVICE_FEATURES_SEL` and `DRIVER_FEATURES_SEL` choose low/high feature words.
- Modern driver features are staged in `proxy->guest_features[]` and committed when `FEATURES_OK` is written to status.
- Queue size is written to QEMU's virtqueue and cached in `proxy->vqs[]` for modern mode.
- Modern `QUEUE_READY` installs cached queue addresses and enables the queue.
- `QUEUE_NOTIFY` optionally stores notification data shadow avail index when `VIRTIO_F_NOTIFICATION_DATA` is negotiated, then calls `virtio_queue_notify()`.

Interrupts and ioeventfd:
- `INTERRUPT_STATUS` reads the virtio ISR; `INTERRUPT_ACK` clears bits and updates IRQ.
- `virtio_mmio_update_irq()` asserts the IRQ when ISR is nonzero.
- `ioeventfd` registers eventfds on `VIRTIO_MMIO_QUEUE_NOTIFY`, unless record/replay mode disables fd-based ioevents.
- VM running/stopped callbacks start and stop ioeventfd.

Migration:
- Legacy transport config migration saves feature selectors and guest page shift.
- Modern extra-state subsection saves staged guest feature words and all per-queue modern state: queue size, enabled flag, descriptor/avail/used address words.
- Extra state is migrated only for non-legacy devices.

Type and bus behavior:
- `TYPE_VIRTIO_MMIO` is a sysbus device with properties `force-legacy` and `ioeventfd`.
- `TYPE_VIRTIO_MMIO_BUS` allows one child device and reports a path derived from the MMIO address.
- `virtio_mmio_pre_plugged()` adds `VIRTIO_F_VERSION_1` for non-legacy backends.
- The bus advertises variable vring alignment.

Important invariants:
- Legacy-only and modern-only registers are rejected with guest-error logs when accessed in the wrong mode.
- Status writes stop ioeventfd before clearing `DRIVER_OK` and restart it after setting `DRIVER_OK`.
- Writing status zero performs a transport soft reset.
- Guest notifier setup rolls back already assigned notifiers if a later assignment fails.
- Modern queue enabled state is transport state and must be migrated.

Filesystem/block relevance:
- This is a transport used by MMIO virtio devices, including storage-related virtio devices on non-PCI machines. Correct queue/register behavior is required for virtual block and filesystem transports.

Notable risks:
- Shared memory selector registers are effectively unimplemented and length reads return all ones to indicate no region.
- The code logs many guest misuse cases but often continues by returning zero or ignoring writes.
- KVM irqfd is explicitly not used here for guest notifiers.
