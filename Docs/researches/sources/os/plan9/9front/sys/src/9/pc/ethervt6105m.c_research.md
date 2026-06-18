# File Research: sources/os/plan9/9front/sys/src/9/pc/ethervt6105m.c

Implements a separate Ethernet driver for the VIA VT6105M Rhine III-M Fast Ethernet controller, registered as `vt6105M`.

Key elements:
- Closely resembles `ethervt6102.c` but targets PCI ID `0x1106:0x3053` and adds Rhine III-M-specific registers, checksum bits, queue wake register definitions, and debug register dumping.
- Uses hardware descriptor rings with `Ds` containing hardware fields plus software `Block` and ring links. RX descriptors include checksum offload control/status bits.
- Defines larger rings than VT6102: `Nrd = 196`, `Ntd = 128`, with receive buffer size `ETHERMAXTU + Crcsz + Bslop`.
- Uses a `Bpool` for receive buffers instead of allocating each RX block directly. This reduces repeated allocation overhead and keeps receive buffers aligned.
- `vt6105Mreset()` resets power management state, reloads EEPROM MAC address, configures DMA as store-and-forward style (`DmaSAF`), accepts broadcast/multicast, initializes MII, and triggers autonegotiation if link status is unavailable.
- `vt6105Mattach()` allocates descriptor memory, grows the RX block pool, sets up RX descriptors with IP/TCP/UDP checksum request bits, configures TX descriptors, starts the NIC, waits briefly for link, enables TX/RX, and launches the link process.
- `vt6105Mreceive()` handles checksum offload results by setting `Btcpck`, `Budpck`, and `Bipck` flags before passing packets to `etheriq()`.
- `vt6105Mtransmit()` queues packets directly without the VT6102 bounce-prefix split logic, uses `Tdctl` to suppress most TX interrupts, and tracks max TX ring occupancy and timing.
- `vt6105Minterrupt()` services RX, TX, link, and error causes, accounts abort/underflow counters, raises TX FIFO threshold on underflow, and uses cycle accounting.
- `vt6105Mifstat()` reports error counters, RX/TX interrupt counters, checksum counts, total cycle time, register snapshots, and PHY registers.
- `edev->maxmtu` is set to `ETHERMAXTU + Bslop`, and `edev->mbps` is set to 1000 as a queue-sizing workaround even though the hardware is Fast Ethernet.

Filesystem relevance: none directly. It is a kernel PCI Ethernet driver and is useful as an example of 9front DMA rings, block pools, RX checksum offload propagation, interrupt deferral, and MII link management.
