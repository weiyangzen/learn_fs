# File Research: sources/os/bsd/openbsd-src/sys/sys/intrmap.h

This header declares the interrupt-to-CPU mapping abstraction.

Key definitions:
- Opaque `struct intrmap`.
- Flag: `INTRMAP_POWEROF2`.

APIs:
- `intrmap_create`
- `intrmap_destroy`
- `intrmap_count`
- `intrmap_cpu`

Behavior and integration:
- Maps device interrupts over a CPU set/count.
- Takes `const struct device *` at creation and returns `struct cpu_info *` for an interrupt index.

Risk notes:
- `INTRMAP_POWEROF2` likely constrains mapping count/selection to power-of-two behavior; callers must pass flags consistent with device interrupt layout.
