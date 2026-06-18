# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/list.c

## Scope

Formatting and diagnostics for `5l`.

## Behavior

- Installs custom formatters for opcodes, conditions, addresses, programs, symbols, and string constants.
- `Pconv()` formats linker instructions.
- `Dconv()`/`Nconv()` render ARM address modes, symbols, stack references, constants, shifts, branches, FP constants, and string constants.
- `diag()` prints errors with current function context and exits after too many errors.

## Dependencies

Uses `l.h`, `anames[]`, linker globals, and floating conversion helpers.

## Risks And Invariants

- Formatting uses fixed `STRINGSZ` local buffers.
- `Sconv()` prints only `sizeof(long)` bytes from string constants, matching old object string constant conventions.
