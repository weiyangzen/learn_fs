# File Research: sources/os/plan9/9front/sys/src/9/pc/ethervirtio.c

Implements a Plan 9 virtio-net driver for the legacy/transitional virtio PCI interface.

Key behavior:
- Defines legacy virtio PCI register layout, device status bits, feature bits, descriptor flags, virtqueue structs, net header, and control queue command classes.
- Probes vendor `0x1AF4` virtio-net devices with device IDs `0x1000` or `0x1041`, revision `0`, I/O BAR0, and subsystem type `1`.
- Performs legacy initialization: reset status, acknowledge driver, negotiate `Fmac`, `Fstatus`, `Fctrlvq`, and `Fctrlrx`, initialize RX/TX/control virtqueues, and publish queue PFNs.
- Allocates each virtqueue in legacy split-ring layout with descriptor, avail, and used areas aligned to 4096 bytes.
- Attach sets `Sdriverok` and starts RX/TX kprocs.
- RX kproc prebuilds descriptor pairs for virtio net header plus writable packet buffer, replenishes from a block pool, notifies the device, sleeps for used entries, and passes received packets to `etheriq`.
- TX kproc prebuilds descriptor pairs for shared header plus packet data, reads from `edev->oq`, waits for free slots, retires used descriptors, and notifies the device.
- Interrupt handler reads ISR and wakes any virtqueue with new used entries.
- Control queue helper sends class/cmd/data/ack descriptor chains for promiscuous and all-multicast control when supported.
- `ifstat` prints feature/status registers and queue counters; shutdown resets status and clears PCI bus mastering.

Dependencies:
- Uses Plan 9 PCI, I/O port, Ethernet, block pool, rendezvous, kproc, and DMA physical address APIs.
- Implements legacy virtio 1.0 split virtqueue behavior, not modern non-transitional PCI capability layout.

Research notes:
- Non-transitional virtio devices are explicitly skipped and expected to be handled by `ethervirtio10`.
- RX and TX use a single shared virtio header allocation per queue because header contents are not varied.
- Link is set optimistically to up in `reset`; `Fstatus` is only reported in `ifstat`, not used to drive link changes.
