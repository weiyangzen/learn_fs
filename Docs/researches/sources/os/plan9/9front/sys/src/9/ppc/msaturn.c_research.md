# File Research: sources/os/plan9/9front/sys/src/9/ppc/msaturn.c

Saturn/UCU board machine initialization and interrupt controller support.

Key responsibilities:
- Defines Saturn interrupt-controller registers and maps hardware interrupt priority slots to Plan 9 vectors.
- Initializes interrupt masks/priorities, enables/disables vectors, reads interrupt acknowledge register, and acknowledges interrupts.
- Initializes machine state, CPU/bus frequencies, active CPU state, machine checks, cache/L2-related state, FP state, HID0 bits, and a built-in plan9.ini string.
- Provides empty shared-segment initialization, trap-vector installation, and reboot stub.

Dependencies:
- Uses UCU/Saturn register constants, PPC special-register helpers, and shared trap/interrupt infrastructure.

Notable behavior:
- Supports a narrow set of active vectors: timer, UART0, and Ethernet.
