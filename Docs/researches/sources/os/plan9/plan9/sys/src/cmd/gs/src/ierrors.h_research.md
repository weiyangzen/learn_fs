# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ierrors.h

Defines interpreter-level Ghostscript error codes and error-name lists.

Key points:
- Explicitly warns this is interpreter-only; graphics library code should use `gserrors.h`.
- Uses non-negative returns for success and negative integers for failures.
- Declares `gs_error_names[]`, populated from `ERROR_NAMES` in `iinit.c`.
- Defines Level 1 PostScript errors from `e_unknownerror (-1)` through `e_VMerror (-25)`.
- Defines Level 2/DPS additions: `e_configurationerror`, `e_invalidcontext`, `e_undefinedresource`, `e_unregistered`, and NeXT DPS `e_invalidid`.
- Defines internal pseudo-errors for fatal/quit/interpreter exit, color remap retry, exec-stack underflow, VM reclaim, incremental input, stdio callouts, and usage-info exit.
- `ERROR_IS_INTERRUPT(ecode)` treats `e_interrupt` and `e_timeout` as re-execute cases.

Research relevance:
- Central interpreter control-flow contract for PostScript errors, normal quits, fatal exits, GC-triggering VM reclaim, input suspension, and console callouts.
