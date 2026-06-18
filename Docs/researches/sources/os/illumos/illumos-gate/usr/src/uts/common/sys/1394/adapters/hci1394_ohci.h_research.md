# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_ohci.h

This large private header defines the OpenHCI register interface, register layout, access macros, and exported OHCI helper routines for the `hci1394` HAL.

Content categories:
- Timing, buffer, cookie, bus cycle, timestamp, and register address constants.
- PHY register bit definitions.
- OpenHCI event/ACK codes.
- Interrupt event/mask bits for async, isoch, self-ID, bus reset, PHY, cycle, and fatal conditions.
- Link control, host control, node ID, PHY control, context control, bus options, config ROM, CSR, retry, GUID, and self-ID field masks.
- Helpers for classifying async receive response/request tcodes.
- Macros writing IR/IT context control and match registers through `ddi_put32`.
- Macros reading isoch context active/run/cmd pointer state through `ddi_get32`.

Main structures:
- `hci1394_ctxt_regs_t`: generic context control/command pointer register block.
- `hci1394_ir_ctxt_regs_t`: isoch receive context registers, adding `ctxt_match`.
- `hci1394_regs_t`: full OpenHCI memory-mapped register layout, including global registers, async contexts, and arrays of IT/IR contexts.
- `hci1394_ohci_t`: private OHCI state containing config ROM/self-ID buffers, cached PHY settings, bus time tracking, PHY type, driver info, register handle/pointer, mutex for atomic hardware operations, and soft-state backpointer.

Key APIs:
- Init/fini/resume/startup/soft reset.
- Raw register and PHY access.
- Interrupt master and per-class enable/disable/clear/asserted helpers.
- IT/IR context count and command pointer setup.
- Link, bus reset, CSR read/compare-swap, posted write address, contender/root holdoff/gap count, PHY filtering, config ROM update, self-ID management, node ID, cycle/bus time, AT retry controls, cycle/PHY ISRs, root/CMC checks, bus capabilities, and async context start/wake/stop routines.

Research notes:
- `ohci_mutex` serializes PHY, CSR compare-swap, and read/modify/write hardware operations.
- `OHCI_BOPT_PMC` is defined with the same bit value as `OHCI_BOPT_IRMC`, which is worth verifying against the OpenHCI/1394 bus options spec before using as power-manager capability.
