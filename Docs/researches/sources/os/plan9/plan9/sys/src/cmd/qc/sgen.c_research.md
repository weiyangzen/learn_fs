# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/sgen.c

Expression addressability and complexity analysis for PowerPC code generation.

Key responsibilities:
- Emits synthetic no-op uses of return registers for functions with no explicit return value.
- Computes `Node.addable` classes for constants, names, registers, indirect registers, addresses, dereferences, and address-plus-constant forms.
- Computes `Node.complex`, estimating temporary register pressure.
- Rewrites power-of-two multiplies/divides/modulos into shifts or masks.
- Normalizes immediate-friendly operations by moving constants to the right side and inverting relations when needed.
- Marks function calls as high complexity.

Dependencies:
- Uses generic compiler AST/type infrastructure from `gc.h`, including `vlog`, `simplifyshift`, `com64`, and type classification tables.

Notable risks:
- Addressability classes are numeric conventions consumed by later code generation.
- Rewrites happen before final code selection, so missed simplifications can generate worse code while unsafe rewrites can miscompile.
