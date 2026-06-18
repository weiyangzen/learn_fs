# File Research: sources/os/bsd/netbsd-src/sys/sys/biohist.h

## Scope

Wraps `kernhist` tracing for buffer I/O history logging.

## APIs And Behavior

- If `BIOHIST_PRINT` is set, forces `KERNHIST_PRINT`.
- When `BIOHIST` is enabled, maps `BIOHIST_DECL`, `DEFINE`, `INIT`, `INITIALIZER`, `LINK_STATIC`, `LOG`, `CALLED`, `CALLARGS`, and `FUNC` to corresponding `KERNHIST_*` macros.
- Defines default `BIOHIST_SIZE` as 500 if not provided.
- When disabled, all macros expand to no-ops.
- Declares global `biohist`.

## Dependencies

- Includes optional `opt_biohist.h` and `sys/kernhist.h`.

## Risks And Invariants

- Compile-time options entirely control whether logging exists.
- Format and argument macros inherit `kernhist` semantics.
