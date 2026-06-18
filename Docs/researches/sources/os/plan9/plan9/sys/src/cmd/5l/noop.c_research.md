# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/noop.c

## Scope

Late instruction-list normalization for `5l`.

## Behavior

- Removes NOPs, follows through branch targets past NOPs, detects leaf functions, records frame/become sizes, and emits prologue/epilogue sequences.
- Expands `RET` and special `BECOME` forms into ARM branch/load sequences.
- Rewrites integer division/modulo pseudo-ops into calls to helper routines `_div`, `_divu`, `_mod`, and `_modu`.
- Includes compatibility fixup for old unsigned-to-double code compiled with earlier `5c`.
- Initializes division helper symbols for static and dynamically loadable module modes.

## Dependencies

Uses `l.h`, `prg()`, symbol lookup, text list globals, and helper symbols from object loading.

## Risks And Invariants

- Prologue/epilogue generation assumes Plan 9 ARM stack conventions and link register save/restore forms.
- Division pseudo-op expansion mutates a single instruction into a multi-instruction call sequence and uses `REGTMP`.
- DLM mode can mark helper routines as imports.
