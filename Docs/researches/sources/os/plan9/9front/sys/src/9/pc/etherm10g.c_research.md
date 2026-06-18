# File Research: sources/os/plan9/9front/sys/src/9/pc/etherm10g.c

Implements a firmware-driven Plan 9 driver for Myricom 10G PCIe Ethernet adapters.

Key behavior:
- Embeds 2K/4K Myricom firmware images and chooses firmware/alignment from PCIe lane/ECRC checks and optional `myriforce`.
- Maps adapter RAM, parses EEPROM strings for MAC address and serial number, allocates DMA-visible command, completion, stats, TX, and RX structures.
- Boots firmware by copying it into adapter RAM and submitting firmware boot commands through device command ports.
- Sends device commands for reset, interrupt queue DMA, ring offsets/sizes, coalescing, stats DMA, MTU, MAC address, flow control, promiscuous mode, and multicast join/leave.
- Uses a completion ring plus separate small and big RX rings; RX kproc replenishes both and delivers completed packets from the done ring.
- TX path segments outgoing blocks on firmware alignment boundaries, fills host TX descriptors, copies them into LANai/device memory, and frees blocks after firmware TX count advances.
- Interrupt handler wakes RX/TX workers, handles MSI versus legacy interrupt acknowledgement, checks DMA-updated stats, and updates link state.
- Exposes `ifstat` for firmware stats/ring counters and ctl commands for debug, coalescing, forced wakeups, and RX ring dump.
- Registers as `m10g` for Myricom PCI vendor IDs.

Dependencies:
- Uses Plan 9 PCI, Ether, block pool, kproc, DMA address, and command parsing APIs.
- Depends on Myricom firmware command ABI and device RAM layout.

Research notes:
- The device is treated as big-endian; helper functions pack/unpack 16/32-bit values.
- Shutdown/detach path unmaps and frees the controller and is marked/incomplete in spirit.
- Potential bug: `whichfw` uses `if(i != 4*KiB || i != 2*KiB)`, which is always true and forces 2KiB for any `myriforce` value.
