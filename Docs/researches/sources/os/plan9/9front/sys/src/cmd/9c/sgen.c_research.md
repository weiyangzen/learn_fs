# File Research: sources/os/plan9/9front/sys/src/cmd/9c/sgen.c

High-level statement/codegen preparation support for the PowerPC64 C compiler backend.

Key functions:
- `noretval` emits dummy uses of integer/floating return registers when a function must not return a value of those classes.
- `xcom` computes node addressability and register complexity, classifying constants, names, registers, indirect registers, address-of, indirection, and address arithmetic.
- Rewrites multiply/divide/modulo by powers of two into shifts or masks for unsigned cases and assignment variants.
- Calls `simplifyshift` after shift-generating rewrites.
- Marks function calls as high complexity (`FNX`).
- Normalizes immediate-friendly comparisons and commutative arithmetic by moving constants to the right side.
- The file is the machine-specific expression classification layer feeding later `cgen` decisions.

Filesystem relevance: indirect compiler code-generation support.
