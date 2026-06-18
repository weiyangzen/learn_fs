# File Research: sources/os/plan9/9front/sys/src/9/xen/fns.h

Function prototypes and macros for the Xen port.

Purpose:
- Extends shared Plan 9 port prototypes with x86 and Xen-specific declarations.

Key content:
- Declares architecture, CPU, FPU, MMU, trap, interrupt, timer, UART, and process-state functions.
- Defines `KADDR`, `PADDR`, no-op `dcflush`, Xen memory barriers, and `userureg`.
- Declares Xen console, MMU update/pinning, grant-table, event-channel, wall-clock, xenstore, and hypercall wrappers.
- Lists hypervisor calls used by this port: trap table, MMU update, event channel, console, grant table, memory op, shutdown, timer, callbacks, and more.

Integration:
- Central header for Xen C files and assembly cross-references.

Risks/notes:
- Several generic PC hooks remain declared even when Xen implementations are stubs or no-ops.
