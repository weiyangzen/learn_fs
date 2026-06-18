# File Research: sources/os/plan9/plan9/sys/src/9/pc/piix4smbus.c

Intel PIIX4 SMBus controller support.

Key elements:
- Matches Intel vendor `0x8086`, PIIX4 power-management function `0x7113`.
- Defines SMBus PCI config registers and I/O register bits for host/slave status/control, command, address, and data.
- `proto` maps Plan 9 SMBus transaction types to PIIX4 protocol bits, direction, command presence, and byte count.
- `transact` serializes with `qlock`, waits for host idle, attempts `Kill` on stuck transactions, programs address/command/data, starts transaction, polls completion/error bits, and reads returned data.
- `piix4smbus` finds the PCI device, disables SMBus, uses BIOS base if available or allocates I/O ports, disables interrupts, aborts pending work, enables the controller, and returns an `SMBus` interface.

Interactions:
- Uses PCI config helpers from `pci.c`.
- Exposes an `SMBus` protocol object consumed by higher-level SMBus/I2C-like device code.

Research notes:
- Hardware management bus support; may affect sensors/EEPROM/power devices, not filesystem logic directly.
