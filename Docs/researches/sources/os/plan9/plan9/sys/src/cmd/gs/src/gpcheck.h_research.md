# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpcheck.h

Purpose: Defines the portable interrupt-check interface for long-running Ghostscript operations.

Key interfaces: `gs_return_check_interrupt`, optional `gp_check_interrupts`, and macros `process_interrupts`, `return_if_interrupt`, `return_check_interrupt`, and `set_code_on_interrupt`.

Behavior: When `CHECK_INTERRUPTS` is defined, callers periodically invoke platform checks and map positive interrupt results to `gs_error_interrupt`; otherwise all macros compile to no-ops or direct return of the supplied code.

Dependencies: Expects `gs_memory_t`, Ghostscript error constants, and `gs_note_error`.

Risks and notes: Correctness depends on long-running loops calling these macros consistently. Platforms without `CHECK_INTERRUPTS` cannot asynchronously interrupt through this mechanism.
