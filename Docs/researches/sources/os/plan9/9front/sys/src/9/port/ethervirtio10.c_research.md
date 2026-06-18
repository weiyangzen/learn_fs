# File Research: sources/os/plan9/9front/sys/src/9/port/ethervirtio10.c

Implements a non-legacy Virtio 1.0 Ethernet driver for PCI devices that require modern virtio capability-based MMIO access. It targets the case where QEMU disables legacy virtio-net.

The driver discovers virtio PCI capabilities, maps common/device/ISR/notify regions, negotiates features, initializes RX/TX/control virtqueues, and registers an `Ether` device. `attach` enables queues, marks the driver ready, and starts RX/TX kernel processes.

`txproc` consumes blocks from the Ethernet output queue and posts two-descriptor TX chains: virtio net header plus packet. `rxproc` maintains RX buffers, posts them to the receive queue, and forwards completed packets to `etheriq`. `vctlcmd` sends control-queue commands for promiscuous and all-multicast modes.

Interrupt handling wakes queues when used rings advance. `shutdown` clears device status and bus mastering. `ifstat` reports negotiated features, device status, and queue indices/counters. The implementation depends on `virtio10.h`, PCI helpers, DMA-safe ring allocation, and Plan 9 block pools.
