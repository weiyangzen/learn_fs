# File Research: sources/os/plan9/9front/sys/src/cmd/5i/float.c

This file contains floating-point instruction table scaffolding and mostly stubbed floating-point handlers for `5i`.

Key contents:
- Declares many FP operation handlers.
- `cop1[]` maps operation slots to names such as `add.f`, `sub.f`, `mul.f`, `div.f`, `abs.f`, `mov.f`, `neg.f`, conversions, and FP comparisons.
- `unimp()` reports an unimplemented floating-point trap and jumps back through `errjmp`.
- `inval()` reports invalid operation and jumps through `errjmp`.
- `ifmt()` reports invalid FP data format.
- Most execution handlers are empty stubs:
  - arithmetic/conversion/move/compare handlers,
  - load/store FP handlers,
  - coprocessor transfer handlers,
  - branch-on-FP-condition handler,
  - `Icop1()` dispatcher.

Dependencies and interactions:
- Included in `5i` build as part of interpreter instruction support.
- Names and `cop1[]` look inherited from a MIPS-style coprocessor model despite ARM target context.

Research relevance:
- Indicates FP support in `5i` is incomplete/stubbed.

Risk notes:
- Programs relying on floating-point execution through `5i` likely do not run correctly.
- Unimplemented handlers either do nothing or trap depending on which path is reached.
