# File Research: sources/os/plan9/9front/sys/src/9/xen/trap.c

Xen x86 trap, syscall, page-fault, notification, and process-register handling.

Purpose:
- Installs Xen trap table entries and handles x86 exceptions in a paravirtual guest.

Key behavior:
- `trapinit` registers callbacks, installs all 256 vector entries with `HYPERVISOR_set_trap_table`, enables IRQ handling, and installs breakpoint/page-fault/double-fault handlers.
- `trap` routes event-channel IRQs, user exceptions, page faults, diagnostics, and notify/kexit handling.
- `fault386` reads CR2 from Xen shared vcpu info, optionally syncs kernel mappings, then calls VM `fault`.
- `syscall` is called directly from assembly and invokes `dosyscall`.
- `notify`/`noted` implement Plan 9 note delivery and validation of user segment selectors.
- Fork/exec/debug helpers initialize or inspect saved `Ureg` state.
- Safe page-fault handler hooks exist for failsafe callback but currently panic.

Integration:
- Depends on `l.s` vector table, `plan9l.s` syscall entry, Xen shared info, and generic Plan 9 VM/process code.

Risks/notes:
- Safe page-fault support is incomplete.
- Some CR/MSR dumping is deliberately skipped under Xen.
