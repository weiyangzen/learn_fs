# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/sgen.c

## Scope

Small architecture-specific support routines for expression complexity and return-value liveness.

## Behavior

- `noretval()` emits artificial NOP uses of integer and floating return registers so later optimization keeps return values live.
- `xcom()` computes ARM addressability and expression complexity for AST nodes.
- Rewrites multiply/divide/modulo by powers of two into shifts or masks where legal.
- Normalizes commutative immediate expressions so constants land on the preferred side.

## Dependencies

Uses `gc.h`, AST `Node` layout, compiler type tables, and helpers such as `vlog()`, `com64()`, and `complex()`.

## Risks And Invariants

- Addressability is encoded as legacy numeric classes (`2`, `3`, `10`, `11`, `12`, `20`) shared with the rest of `5c`.
- Power-of-two rewrites rely on type semantics and are bypassed for 64-bit composite cases via `com64()`.
