# File Research: sources/os/plan9/9front/sys/src/9/port/portfns.h

Central portable kernel function prototype header.

Key contents:
- Declares process, scheduler, timer, VM, page, segment, channel, device, mount, environment, queue, block, PCI-independent I/O, logging, parsing, random, UART, watchdog, syscall, note, memory allocation, and utility functions.
- Defines the `waserror()`/`poperror()` error-stack macros.
- Defines time conversion macros `MS2NS` and `TK2MS`.
- Declares network byte-order helpers and low-level timing helpers.
- Adds vararg checking for `iprint`, `panic`, and `pprint`.

Role:
- Provides portable C modules with a single shared declaration surface for cross-subsystem calls.

Notable risks:
- Very broad declaration surface means stale prototypes can silently affect many modules.
- Contains a duplicate `ms2tk` declaration.
