# File Research: sources/virtualization/qemu/hw/virtio/virtio-bus.c

## Purpose
Implements the abstract virtio bus support layer used by transports. It coordinates device plug/unplug, feature discovery, config forwarding, ioeventfd ownership, host notifier setup, firmware path delegation, and IOMMU checks.

## Key Elements
- `virtio_bus_device_plugged()` calls transport pre-plug hooks, obtains device features through `get_features_ex` or legacy `get_features`, invokes transport `device_plugged`, and sets DMA address space/IOMMU feature state.
- `virtio_bus_reset()` stops ioeventfd and resets the attached virtio device.
- Config helpers forward get/set config, bad-features, device id, and config length requests to the attached `VirtIODevice`.
- `virtio_bus_grab_ioeventfd()` and `virtio_bus_release_ioeventfd()` implement shared ownership so vhost can temporarily take ioeventfd control.
- `virtio_bus_start_ioeventfd()` and `virtio_bus_stop_ioeventfd()` delegate to device `start_ioeventfd`/`stop_ioeventfd` when the transport supports assignment and ownership is not grabbed.
- `virtio_bus_set_host_notifier()` initializes/assigns/unassigns host notifiers and updates virtqueue notifier enabled state.
- `virtio_bus_cleanup_host_notifier()` drains and destroys an event notifier after assignment is removed.
- Class init delegates device paths to the parent proxy.

## Dependencies
Uses QEMU virtio device APIs, address-space globals, qdev bus infrastructure, event notifiers, and transport callbacks supplied by `VirtioBusClass`.

## Behavior/Risks
- IOMMU platform handling fails plug when the transport DMA address space is not system memory and the device did not retain `VIRTIO_F_IOMMU_PLATFORM`.
- `ioeventfd_started` is preserved when grabbed so release can restart ioeventfd.
- Host notifier cleanup must happen after assignment is disabled and pending events are drained.
