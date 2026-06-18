# File Research: sources/os/plan9/9front/sys/src/cmd/2c/sgen.c

Purpose: statement-level code generation and expression complexity/addressability analysis.

Key behavior:
- `codgen()` emits an `ATEXT` pseudo-op for a function, calls `gen()` for the body, warns on missing return, emits fallback return, then invokes `regopt()`.
- `gen()` handles statement trees: lists, returns, labels/gotos, cases/defaults, switches, while/do/for loops, continue/break, if/else, used/set pseudo-statements, and default expression statements.
- Maintains `breakpc`, `continpc`, `nbreak`, `cases`, `retok`, and patch lists for structured control flow.
- `usedset()` emits no-op tests to influence volatile/used/set analysis.
- `noretval()` emits dead tests of return registers so the optimizer knows which return registers are live/dead.
- `xcom()` computes `complex` and `addable` values, performs local tree rewrites, detects indexed-address opportunities, rewrites power-of-two multiply/divide to shifts, and orders operands for cheaper code.
- `indx()` selects base/index/scale pieces for 68020 indexed addressing.
- `bcomplex()` prepares boolean control-flow generation; `nodconst()` encodes small constants through pointer casts for legacy APIs.

Research notes:
- Addability classes are target-specific numeric categories used throughout `cgen.c` and `txt.c`.
- Switch generation is split: `gen()` collects cases and calls `doswit()` in `swt.c`.
