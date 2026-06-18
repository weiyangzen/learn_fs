# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ierrors.h

Defines interpreter-level error codes and error-name lists for Ghostscript.

Key points:
- Explicitly warns this is interpreter-only; graphics library code should use `gserrors.h`.
- Uses negative integer codes for failures and non-negative values for success.
- Declares `gs_error_names[]`, populated in `iinit.c`.
- Defines Level 1 PostScript errors from `e_unknownerror (-1)` through `e_VMerror (-25)`.
- Defines Level 2/DPS additions: `e_configurationerror`, `e_invalidcontext`, `e_undefinedresource`, `e_unregistered`, `e_invalidid`.
- Defines pseudo-errors used internally:
  - `e_Fatal`, `e_Quit`, `e_InterpreterExit`
  - `e_RemapColor`
  - `e_ExecStackUnderflow`
  - `e_VMreclaim`
  - `e_NeedInput`, `e_NeedStdin`, `e_NeedStdout`, `e_NeedStderr`
  - `e_Info`
- `ERROR_IS_INTERRUPT(ecode)` treats `e_interrupt` and `e_timeout` as retry/re-execute cases.

Dependencies and interactions:
- `iinit.c` builds `gs_error_names[]` from `ERROR_NAMES`.
- `imain.c` handles `e_NeedStdin/stdout/stderr`, `e_Fatal`, `e_Quit`, and finalization paths.
- Many interpreter modules return these codes as canonical PostScript/interpreter errors.

Research relevance:
- This is the central error-code contract for interpreter control flow, including normal quits, fatal exits, VM reclaim, input suspension, and console callouts.
