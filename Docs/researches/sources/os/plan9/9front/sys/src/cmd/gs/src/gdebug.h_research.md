# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdebug.h

## Scope

Ghostscript debug/tracing macro definitions.

## Key Behavior

- Declares `gs_debug[128]` and `gs_debug_c`, with uppercase flags enabling corresponding lowercase flags.
- Aliases `gs_log_errors` to `gs_debug['#']`.
- Redirects diagnostic streams to `gs_debug_out` when `DEBUG` is enabled.
- Defines `if_debug0` through `if_debug12` macros that compile to debug printing under `DEBUG` and `DO_NOTHING` otherwise.
- Declares byte, bitmap, and string debug dump helpers.

## Dependencies

Depends on Ghostscript debug print helpers such as `dlprintfN`, `dprintfN`, and `DO_NOTHING`.

## Risks And Invariants

- Debug code inclusion is compile-unit-specific via `DEBUG`; runtime output still depends on flags.
- `gs_debug_c` flag semantics are relied on by many call sites for selective tracing.
