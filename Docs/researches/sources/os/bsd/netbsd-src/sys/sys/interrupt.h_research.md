# File Research: sources/os/bsd/netbsd-src/sys/sys/interrupt.h

Defines the machine-independent interrupt-distribution interface built on `sys/intr.h` and kernel CPU sets. It introduces fixed-size interrupt identifiers via `intrid_t`, a variable-length `intrids_handler`, and APIs for interrupt counters, device names, assigned/available CPUs, interrupt ID construction/destruction, and CPU-affinity distribution.

The file is a declaration-only kernel/user ABI surface for interrupt management tools. Key risks are ABI sizing around `INTRIDBUF`, the flexible one-element `iih_intrids` tail, and correctness of callers passing valid `kcpuset_t` masks for interrupt affinity changes.
