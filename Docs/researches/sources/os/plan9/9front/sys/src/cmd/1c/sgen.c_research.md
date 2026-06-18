# File Research: sources/os/plan9/9front/sys/src/cmd/1c/sgen.c

Statement-level code generation and addressability analysis for `1c`.

Key responsibilities:
- `codgen` emits a function `ATEXT`, generates its body, checks missing returns, emits return cleanup, and invokes register optimization.
- `gen` lowers statements: lists, returns, labels, gotos, cases, switches, loops, breaks/continues, if/else, and used/set pseudo-ops.
- Maintains `breakpc`, `continpc`, `nbreak`, `retok`, stack markers, and case lists.
- `xcom` computes addressability and expression complexity, folding address patterns, constants, power-of-two multiply/divide into shifts, and simple assignment/addressable cases.
- Reorders symmetric and relational expressions to simplify right operands or exploit short immediate encodings.
- `bcomplex` prepares boolean tests and emits branch setup.
- `nodconst` encodes small constants through pointer casts used by backend helper APIs.

Notable details:
- Addressability classes are target-specific and drive later `cgen` decisions.
- Short/byte multiply/divide assignment is widened to long/unsigned long because the target lacks direct byte/short forms.
