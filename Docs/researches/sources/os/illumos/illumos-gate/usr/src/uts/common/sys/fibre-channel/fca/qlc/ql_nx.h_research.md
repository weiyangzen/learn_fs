# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_nx.h

## Role

`ql_nx.h` defines NetXen/82xx-style hardware support used by the `qlc` driver. It describes chip revisions, firmware/device state handshakes, CRB/register address maps, PCI/windowing rules, ROM/flash access constants, interrupt register mappings, and minidump template formats.

## Major Definitions

The file includes:
- P3/P3-plus revision constants and revision test macros.
- Phantom firmware initialization states and host acknowledgement values.
- Device state values such as poll, cold, initializing, ready, need reset, need quiescent, failed, and quiescent.
- CRB/NIC register offsets for command producer/consumer indexes, pause buffers, firmware command/argument registers, command and receive PEG state, interrupt coalescing, RX/TX packet timers, XG state, DMA shift, link speed, software interrupt masks, capabilities, MSI mode, and virtual-port mappings.
- Extensive CRB hub/agent address mapping tables and macros for transforming hardware address spaces.
- ROMUSB/ROM controller registers and SPI ROM instruction opcodes.
- PCI/PCIe memory windows, 128 MB and 2 MB address ranges, CRB windows, direct and indirect addressing helpers, MSI-X table constants, PCI IDs, and interrupt target/mask registers.
- `NX_LEGACY_INTR_CONFIG`, a static initializer for legacy interrupt vector and target-mask/status register mappings across functions.
- Flash and firmware offsets, board info magic, bootloader/image start offsets, and firmware size offset.
- CRB lock, ROM lock, IDC lock, and firmware reset acknowledgement timeout constants.

## Minidump Support

The latter part defines NetXen mini-dump metadata:
- Template command options for size-only versus full-template retrieval.
- Entry type constants for CRB, MUX, queue, board, SRE, OCM, processor registers, caches, stacks, ROM, memory, control entries, and end markers.
- `md_template_hdr_t`, `md_entry_hdr_t`, generic `md_entry_t`, and specialized read/control entry structures for CRB, cache, OCM, memory, ROM, MUX, queue, and control operations.
- Driver flag bits for skipped entries and size errors.
- Control opcodes for write, read/write, AND, OR, poll, read state, write state, and modify state.
- MIU test-agent registers used by minidump memory reads.

## Interfaces

The exported `ql_nx.c` prototypes cover:
- 82xx 32-bit register read/write.
- Chip reset and firmware reload/check/reset.
- Hardware and firmware interrupt clear/enable/disable.
- CRB interrupt pointer updates.
- ROM read/write/erase/status-register write.
- Driver-active state set/clear.
- IDC event handling and polling.
- Request-in register writes.
- Mini-dump template retrieval.

## Integration Notes

This header is highly hardware-specific and depends on macros/types defined elsewhere in the `qlc` driver, including `UNM_PCI_CRBSPACE`, `ql_adapter_state_t`, and bit constants. It is the low-level map that lets the Fibre Channel driver manage converged NetXen/QLogic hardware resources shared with NIC functions.
