# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpuhelper.h

Kernel-only per-CPU helper message interface.

Key responsibilities:
- Defines callback type `cpuhelper_cb_t`.
- Defines `struct cpuhelper_msg`, with `lwkt_msg` as the required first field, callback, callback argument pointer, and integer argument.
- Declares helpers to assert CPU context, send helper messages to a CPU, reply, and initialize messages.

Dependencies:
- Kernel-only; includes `sys/msgport.h` and `sys/msgport2.h`.

Notable risks:
- The `lwkt_msg` first-field requirement is an ABI convention with LWKT messaging code.
- Callers must avoid sending work to the wrong CPU context or replying incorrectly.
