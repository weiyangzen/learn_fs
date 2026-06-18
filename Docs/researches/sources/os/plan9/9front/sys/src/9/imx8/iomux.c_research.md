# File Research: sources/os/plan9/9front/sys/src/9/imx8/iomux.c

Role: Table-driven i.MX8 IOMUXC pad, signal, daisy-chain, pad-control, and GPR configuration.

Key responsibilities:
- Defines pad IDs, signal IDs, daisy selector encoding, pad mux alternatives, pad names, and signal names.
- Tracks input daisy selectors for signals like MDIO, PCIe CLKREQ, SAI, and UART RX/RTS.
- Provides pad-control option parsing for voltage select, LVTTL, hysteresis, pull enable, open drain, slew rate, and drive strength.
- `iomuxpad()` resolves pad name, optional signal name, and optional config string, then updates pad control, mux mode/SION, and daisy select registers.
- Supports negated options using `~` in the config string.
- `iomuxgpr()` updates or reads IOMUXC GPR registers.

Dependencies:
- Hard-wired IOMUXC MMIO at `VIRTIO + 0x330000`.
- Used by every board-level peripheral setup file.

Notes and risks:
- Unknown pad/signal names or unmuxable combinations panic.
- Table includes source spelling quirks such as `SAY6_TX_SYNC` and `RANWNAD_DATA04`; callers must use the corresponding string table names.
