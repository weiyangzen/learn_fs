# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfigv.h

## Scope

Generated low-level build-option header fragment.

## Key Behavior

- Defines `USE_ASM` as disabled expression `(-0)`.
- Defines `USE_FPU` as enabled expression `(1-0)`.
- Defines `EXTEND_NAMES` as 0.
- Defines `SYSTEM_CONSTANTS_ARE_WRITABLE` as 0.

## Dependencies

Consumed by Ghostscript core configuration headers.

## Risks And Invariants

- Encodes target build assumptions; changing it affects portability and interpreter semantics.
- `SYSTEM_CONSTANTS_ARE_WRITABLE` controls whether system constants can be modified.
