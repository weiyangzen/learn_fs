# File Research: sources/os/plan9/9front/sys/src/cmd/vc/sgen.c

Purpose: Target-specific tree simplification and addressability analysis.

Key behavior:
- `noretval` emits pseudo-uses of integer and/or FP return registers.
- `xcom` computes each node’s `addable` and `complex` values for MIPS code generation.
- Recognizes addressable constants, names, registers, indirect registers, address-of, indirection, and constant-offset additions.
- Rewrites multiplication/division/modulo by powers of two into shifts or masks.
- Swaps immediate-friendly binary operands so constants sit on the right.
- Marks function calls as high complexity (`FNX`) and invokes 64-bit comparison support through `com64`.

Dependencies:
- Uses generic compiler tree helpers from `cc.h`, backend target constants, `simplifyshift`, `vlog`, and `com64`.

Notable details:
- The `addable` scale is target-specific and drives direct addressing versus register-temporary generation in `cgen.c`.
