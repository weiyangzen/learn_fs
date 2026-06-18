# File Research: sources/os/bsd/dragonflybsd/sys/sys/signalvar.h

This header defines kernel signal action state, signal set manipulation macros, and machine-independent/machine-dependent signal function declarations.

Key responsibilities:
- Includes `sys/signal.h`; kernel builds also include process and lock headers.
- Defines `struct sigacts`:
  - per-signal disposition table
  - catch masks
  - source PID/UID info
  - ignored/caught/onstack/intr/reset/nodefer/siginfo/usertramp signal sets
  - refcount and flags
- Defines internal handler sentinels:
  - `SIG_CATCH`
  - `SIG_HOLD`
- Defines kernel `SIGACTION(p, sig)` lookup macro.
- Defines signal set manipulation macros:
  - add/delete
  - atomic add/delete
  - empty/fill
  - member check
  - empty/equality checks
  - OR/AND/NAND operations
  - unmaskable, stop-signal, and continue-signal cleanup helpers
- Defines `sigcantmask`.
- Provides inline `__sigisempty()` and `__sigseteq()`.
- Declares kernel signal functions:
  - process exec/init/kill/group signaling
  - `issignal()`, `iscaught()`, `postsig()`
  - direct process/LWP signal posting
  - trap signal handling
  - machine-dependent `sendsig()` and `sigexit()`
  - checkpoint signal handler hook

Important invariants:
- `SIG_CANTMASK()` removes `SIGKILL` and `SIGSTOP` from a mask.
- Atomic signal-set operations use `atomic_set_int()`/`atomic_clear_int()` on backing words.
- `struct sigacts` is process signal action state, not necessarily resident according to comments.

Research notes:
- This file supplies the macros used by `signal2.h` and kernel signal implementation files.
