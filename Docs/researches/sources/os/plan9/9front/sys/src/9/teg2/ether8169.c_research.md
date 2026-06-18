# File Research: sources/os/plan9/9front/sys/src/9/teg2/ether8169.c

RTL8110/8168/8169 Gigabit Ethernet driver for Tegra/ARM, registered as `rtl8169`. It defines Realtek register maps, descriptor formats, MAC variants, PHY access, multicast hashing, statistics, RX/TX rings, PCI probing, interrupt handling, reset/restart, attach, and Plan 9 `Ether` callbacks.

DMA/cache correctness is central: TX packet data is written back before ownership is given to hardware; RX packet data is invalidated before handing to the network stack; descriptor/ring updates use `coherence`; descriptor/stat buffers are aligned. RX/TX processing is split into kernel processes awakened by interrupt-masked status bits.

Initialization resets the device, allocates 1024 TX and RX descriptors, fills RX buffers from a block pool, configures variant-specific magic registers and burst settings, sets descriptor base addresses, enables interrupts, and starts link handling. Error paths restart the controller on FIFO overrun, receive descriptor unavailable, receive errors, or stalled state. PCI probing matches Realtek IDs, detects PCIe, maps BAR2 directly on TrimSlice, validates hardware MAC version, initializes MII, and enables bus mastering.

Notable coupling: `rtl8169attach` sets `l1ptstable.word` and writes it back so secondary Tegra CPUs can proceed after page-table state is stable.
