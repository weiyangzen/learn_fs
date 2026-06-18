# File Research: sources/os/plan9/plan9/sys/src/9/omap/lexception.s

ARM exception vector stubs and register-save/restore paths for OMAP Plan 9.

Key responsibilities:
- Defines `vectors` trampoline entries and `vtable` target table copied to high vectors by `trapinit()`.
- Handles SWI/syscall directly in `_vsvc`, building a `Ureg`, loading kernel `SB`, `m`, and `up`, calling `syscall()`, then returning via `RFE`.
- Handles undefined instruction, prefetch abort, data abort, IRQ, and FIQ through vector-specific stubs.
- `_vswitch` changes from exception modes to SVC mode, distinguishes kernel versus user exceptions, saves a full `Ureg`, calls `trap()`, and restores state.
- Provides `setr13()` to install per-mode stack pointers.

Important behavior:
- Adjusts banked registers carefully while switching processor modes.
- Uses separate user and kernel exception save paths because user register access uses `.S` forms.
- Avoids ambiguous writeback forms noted in `notes/movm.w`.
- FIQ currently returns immediately or is routed to IRQ in `vtable`.

Dependencies:
- Depends on `arm.s`, `trap()`, `syscall()`, `setR12`, `L1`, `MACHSIZE`, and ARM PSR mode constants.
- Matches `Ureg` layout expected by C trap/syscall code.

Notable risks:
- Correct `Ureg` stack layout is a hard ABI with `trap.c`, `syscall.c`, and `lproc.s`.
- Any mismatch in saved register order would break syscall/trap return.
