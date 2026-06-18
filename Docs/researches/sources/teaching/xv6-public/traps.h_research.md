# File Research: sources/teaching/xv6-public/traps.h

Trap and interrupt number definitions.

Contents:
- x86 processor exception numbers.
- xv6 syscall trap number `T_SYSCALL`.
- Default catchall number.
- IRQ vector base `T_IRQ0`.
- IRQ numbers for timer, keyboard, COM1, IDE, APIC error, and spurious interrupt.

Used by trap setup, device interrupt routing, assembly syscall stubs, and init code.
