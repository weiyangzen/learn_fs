# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/sgen.c

Purpose: backend expression simplification and addressability/complexity analysis.

Key functions:
- `noretval` emits pseudo-use NOPs for integer and floating return registers.
- `xcom` computes node `addable` and `complex` values for code generation.
- It recognizes constants, names, registers, indirect registers, address-of, indirection, additions, calls, and arithmetic rewrites.
- Rewrites multiplication/division/modulo by powers of two into shifts/ands where valid.
- Canonicalizes immediate-friendly operations so constants move to the right side.
- Marks calls as high complexity (`FNX`).

Integration points:
- `cgen.c` relies on `complex` and `addable` to order evaluation safely.
- Uses common compiler helpers such as `vlog`, `simplifyshift`, `com64`, and type tables.

Risks:
- Incorrect complexity can cause register clobbering around function calls.
- Shift/division rewrites must preserve signedness; this file distinguishes logical operations for unsigned cases.
