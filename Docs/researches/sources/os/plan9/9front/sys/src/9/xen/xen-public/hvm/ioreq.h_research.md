# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/ioreq.h

Imported Xen public HVM I/O request ABI.

Purpose:
- Defines shared I/O request pages used between HVM guests, Xen, and device models.

Key content:
- Defines read/write directions, I/O request states, and I/O request types for PIO, MMIO copy, time offset, and invalidate.
- Defines `struct ioreq` with address, data, count, size, event-channel port, state, pointer/data direction flags, and type.
- Defines `struct shared_iopage` and buffered I/O request structures/ring.
- Defines legacy and modern ACPI PM/GPE I/O port locations and compatibility aliases.

Integration:
- HVM device-model ABI; not used by visible 9front PV block/net code.
- `hvm/params.h` references these ACPI location definitions.

Risks/notes:
- Bitfield layout and one-page buffered I/O structure size are ABI constraints.
