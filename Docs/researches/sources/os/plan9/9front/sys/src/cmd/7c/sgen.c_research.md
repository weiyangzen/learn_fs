# File Research: sources/os/plan9/9front/sys/src/cmd/7c/sgen.c

Early shape/complexity analysis and simple lowering preparation for ARM64 code generation.

Key functions:
- `noretval` emits `ANOP` markers identifying unused integer and/or floating return values.
- `xcom` computes `Node.addable` and `Node.complex`, classifying constants, names, registers, indirect registers, address-taking, dereferences, and address arithmetic.
- Rewrites multiplication/division/modulo by powers of two into shifts or masks where legal.
- Calls `simplifyshift` for shift normalization.
- Calls `rolor` for unsigned OR patterns that can become rotates.
- Marks function calls as `FNX` complexity.
- Reorders immediate constants to the right side for comparisons and commutative integer operations when useful.

Addressability model:
- Constants, names, registers, indirect registers, address-of-name, address-of-indirect-register, and dereferenced address constants receive compact numeric addressability classes used by `cgen.c`.

Filesystem relevance: indirect compiler frontend/backend bridge.
