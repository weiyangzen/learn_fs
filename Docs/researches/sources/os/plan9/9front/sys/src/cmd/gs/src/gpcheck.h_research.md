# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpcheck.h

Purpose: Interrupt-check interface for long-running Ghostscript operations.

Key behavior: Declares `gs_return_check_interrupt`. When `CHECK_INTERRUPTS` is defined, declares `gp_check_interrupts` and provides macros to process, return on, or store interrupt status. A positive interrupt result maps to `gs_error_interrupt`; negative results pass through via `gs_note_error`.

Fallback behavior: Without `CHECK_INTERRUPTS`, all interrupt macros become no-ops or return the original code. This keeps call sites portable without platform conditionals.

Dependencies and notes: The comments identify Microsoft Windows as the current platform requiring periodic user-action checks.
