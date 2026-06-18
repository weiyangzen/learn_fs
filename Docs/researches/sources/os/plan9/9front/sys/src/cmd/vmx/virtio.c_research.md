# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/virtio.c

This file implements legacy PCI virtio queue handling plus virtio-net and virtio-block devices.

Key behavior:
- Defines shared virtio device, queue, and descriptor-chain structures.
- `viogetbuf` waits for DRIVER_OK, validates descriptor chains, maps guest buffers with `gptr`, and tracks live buffers.
- `vioputbuf` writes used-ring entries, wakes reset waiters, and raises PCI interrupts unless suppressed.
- `vioqread`, `vioqwrite`, and `vioqrem` move bytes across readable/writable descriptor segments.
- Implements legacy I/O-port virtio registers for features, queue select/address/size/notify, device status, and ISR status.
- `mkvionet` creates a virtio-net PCI device with RX, TX, and control queues, optional MAC address, file or dialed network backend, feature bits, and RX/TX worker processes.
- Virtio-net supports MAC filtering, multicast/unicast bloom filters, promiscuous/allmulti/alluni/nobcast flags, MAC-table and MAC-address control commands, optional 10-byte host-side packet header, minimum Ethernet padding, and interrupt delivery.
- `mkvioblk` creates a virtio-block PCI device backed by a file, with one queue and a worker supporting read/write sector requests.

Integration and risks:
- Queue reset waits for outstanding live buffers; invalid queue addresses are tolerated but logged.
- Virtio-block computes bounds in bytes from 512-byte sectors and uses simple synchronous file I/O.
- Network backend setup can use Plan 9 `dial` with control operations or a raw file descriptor.
