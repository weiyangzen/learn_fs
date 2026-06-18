# File Research: sources/os/bsd/dragonflybsd/sys/sys/interrupt.h

`interrupt.h` defines system interrupt numbering limits and kernel interrupt registration APIs. It sets maximum hard interrupts to 192, soft interrupts to 64, and derives `FIRST_SOFTINT` and `MAX_INTS`.

It defines `inthand2_t`, soft interrupt numbers in priority order, and corresponding pending-bit masks. Shared aliases include `SWI_CRYPTO` over `SWI_CAMNET`.

Under `_KERNEL`, it declares registration/unregistration for software and hardware interrupts, random interrupt registration, counter access, scheduler entry points for hard/soft interrupt threads, virtual-kernel interrupt hooks, and interrupt-name string tables.
