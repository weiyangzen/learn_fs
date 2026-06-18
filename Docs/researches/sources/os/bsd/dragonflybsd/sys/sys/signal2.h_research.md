# File Research: sources/os/bsd/dragonflybsd/sys/sys/signal2.h

This kernel inline header defines signal-delivery helpers, permission tests, pending-signal computation, conditional all-signal blocking, current-signal selection, and signal-processing reference interlocks.

Key responsibilities:
- Includes kernel process, signalvar, and systm headers.
- Defines `CANSIGNAL(q, sig, initok)`:
  - checks credential trespass
  - checks reaper signal rules
  - allows `SIGCONT` within the same session
- Defines `lwp_sigpend()` to combine process and LWP pending signal sets.
- Defines `lwp_delsig()` to clear LWP pending and optionally process pending state.
- Defines `__sig_condblockallsigs()`:
  - checks per-LWP user-mapped `blockallsigs`
  - marks signal-arrival bit 31
  - masks all maskable signals while preserving unmaskable and synchronous trap signals
- Defines `__cursig()` and macros:
  - `CURSIG`
  - `CURSIG_TRACE`
  - `CURSIG_LCK_TRACE`
  - `CURSIG_NOBLOCK`
- Defines generic signal-processing reference helpers:
  - `sigirefs_hold()`
  - `sigirefs_drop()`
  - `sigirefs_wait()`

Important invariants:
- `lwp_delsig()` requires `p->p_token` and `lp->lwp_spin`.
- `__cursig()` may return with `proc->p_token` held through the `ptok` mechanism.
- Userland `blockallsigs` bit 31 is used as a signal-arrival notification bit.
- `sigirefs_wait()` uses the high bit of `p_sigirefs` as a waiter flag and sleeps on the field.

Research notes:
- This file contains concurrency-sensitive signal delivery logic and userland fast-path integration.
