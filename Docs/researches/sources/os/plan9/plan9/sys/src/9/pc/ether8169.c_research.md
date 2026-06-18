# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8169.c

## Role

Plan 9 PCI Ethernet driver for Realtek RTL8110S/8169S/8168/810x-family controllers. It binds as `rtl8169` and implements device discovery, reset, MII link handling, descriptor-ring RX/TX, multicast filtering, statistics, and shutdown.

## Main Interfaces

- Registers card type with `ether8169link()` via `addethercard("rtl8169", rtl8169pnp)`.
- Exposes generic Ethernet callbacks: `attach`, `transmit`, `interrupt`, `ifstat`, `promiscuous`, `multicast`, and `shutdown`.
- Uses `ethermii.h` for PHY access through `rtl8169miimir`, `rtl8169miimiw`, `rtl8169mii`, and `miistatus`.

## Data Structures

- `D`: 16-byte TX/RX DMA descriptor with control, VLAN, and 64-bit address split fields.
- `Dtcc`: hardware tally counter dump area.
- `Ctlr`: per-device PCI/MMIO state, descriptor rings, buffer arrays, MII state, interrupt mask, statistics, and watermarks.

## Important Behavior

- Scans PCI Ethernet devices and accepts selected Realtek IDs plus one Corega alias.
- Uses I/O-port CSR access rather than memory-mapped access.
- Reads MAC address from `Idr0` unless user supplied an address.
- Allocates 32 TX descriptors, 256 RX descriptors, and a tally-counter block on first attach.
- RX path accepts only single-descriptor packets with `Fs|Ls` and no receive-summary error; CRC is stripped by subtracting four bytes.
- TX path reclaims completed descriptors, queues packets from `edev->oq`, and pokes `Tppoll`.
- Multicast uses Ethernet CRC hash into Realtek multicast registers, with PCIe variants requiring reversed hash-register byte order.
- Hardware-specific setup branches on `macv` and `pciv`, including several undocumented “magic” register writes.

## Dependencies And Assumptions

- Depends on Plan 9 kernel networking (`etherif.h`, `netif.h`) and MII support (`ethermii.h`).
- Assumes 32-bit PCI DMA addresses by writing high descriptor address words as zero.
- Assumes Realtek PHY address `1`.
- Some variants are explicitly untested or rely on vendor-driver-derived constants.

## Notable Risks

- RX fragment handling drops packets that span multiple descriptors; oversized packets are expected to be filtered or counted.
- `rtl8169attach()` calls `miistatus(ctlr->mii)` even though `rtl8169mii()` can fail, so nil MII handling depends on external behavior.
- Hardware-version handling is conservative; unknown `macv` rejects the device.
- Transmit interrupt masking leaves normal TX interrupts mostly off and relies on transmit calls/selected errors for cleanup.
