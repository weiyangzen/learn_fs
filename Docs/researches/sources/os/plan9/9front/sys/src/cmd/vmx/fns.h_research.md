# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/fns.h

This is the shared function/macro declaration header for VMX.

Key contents:
- Declares allocation, kernel loading, register get/set, VM exit handling, timers, VM errors/debug, control operations, MMIO, IRQ, exceptions, VGA, UART, notifications, PCI, guest memory mapping, disk/net device creation, x86 access/step, and I/O helpers.
- Defines `MIN`, `MAX`, `vmdebug`, and unaligned-looking `GET*`/`PUT*` memory access macros.

Integration and risks:
- The `GET*`/`PUT*` macros cast directly to integer pointers, assuming the host tolerates these accesses and using host endian layout.
- Function prototypes connect nearly every VMX device file.
