# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/params.h

Imported Xen public HVM parameter index definitions.

Purpose:
- Defines the HVM parameter namespace for `HVMOP_set_param` and `HVMOP_get_param`.

Key content:
- Defines callback IRQ delivery parameter and encoding.
- Defines xenstore PFN/event-channel convenience params, PAE, ioreq PFNs, buffered ioreq PFN/event channel, Viridian, timer mode, HPET, identity page table, device-model domain, ACPI S state, VM86 TSS, VPT alignment, console PFN/event channel, ACPI I/O port location, memory event params, nested HVM, mem-event ring PFNs, triple-fault reason, and `HVM_NR_PARAMS`.
- Defines virtual timer mode constants and memory-event mode flags.

Integration:
- HVM guest/device-model ABI; not on the visible 9front PV runtime path.
- Depends on `hvm_op.h` and references `features.h`/`ioreq.h` semantics.

Risks/notes:
- Parameter numbers are stable ABI; wrong indices affect guest boot, event delivery, xenstore, or device-model communication.
