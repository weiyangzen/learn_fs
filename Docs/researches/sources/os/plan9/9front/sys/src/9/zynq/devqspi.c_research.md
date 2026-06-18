# File Research: sources/os/plan9/9front/sys/src/9/zynq/devqspi.c

Purpose: Zynq QSPI flash device driver exposed as `#Q/qspi`, with a `boot` file representing the boot flash area.

Key behavior:
- Maps QSPI controller registers and configures linear QSPI mode off/manual SPI mode on.
- `qspicmd` sends 1-4 byte commands and returns RX data.
- `doread` issues fast-read command `0x6B` with dummy cycle and reads up to 16 MiB.
- `dowrite` issues write-enable and quad page-program `0x32` in 256-byte chunks.
- `doerase` erases sector/block at an address.
- Opening `boot` with truncate erases address 0; reads/writes are serialized by `qspil`.

Integration notes: Uses Plan 9 device framework and `vmap`.

Risk/attention points: Buffer addresses must be word aligned. Partial write handling is delicate; the short tail path passes a variable that should be reviewed if arbitrary byte counts are expected.
