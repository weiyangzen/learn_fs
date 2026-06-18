# File Research: sources/os/bsd/dragonflybsd/sys/sys/thread2.h

Inline LWKT critical-section, token-test, CPU-sync, and IPI helper routines.

Key contents:
- Kernel-only header including `systm.h`, `globaldata.h`, `cpumask.h`, and machine CPU functions.
- Defines raw critical count adjustment helpers with CPU compiler fences:
  - `crit_enter_raw`
  - `crit_exit_raw`
- Defines token ownership tests:
  - `_lwkt_token_held_any`
  - `_lwkt_token_held_excl`
- Provides debug and non-debug critical-section macros.
- Implements debug critical enter/exit tracking when `DEBUG_CRIT_SECTIONS` is enabled.
- Defines inline critical-section entry/exit variants:
  - normal
  - quick
  - hard
  - no-yield
- Defines helpers:
  - `crit_test`
  - `lwkt_runnable`
  - `lwkt_getpri`
  - `lwkt_getpri_self`
  - `lwkt_passive_recover`
  - `lwkt_cpusync_init`
  - IPI wrapper variants for one/two/three args, masks, passive sends, and by-CPU sends
  - `lwkt_need_ipiq_process`

Important behavior:
- Critical count increments/decrements are fenced because compiler reordering would break preemption semantics.
- Normal critical sections defer preemption but permit explicit blocking/switching.
- Hard critical sections also disallow blockable operations and raise interrupt nesting level.
- Non-debug `crit_exit()` intentionally wraps in a function to avoid inline code bloat.
- IPI wrappers cast simpler callback signatures to the full three-argument IPI function type.

Research notes:
- This header is hot-path inline support for `thread.h`.
- The comments distinguish software preemption control from physically disabling interrupts.
