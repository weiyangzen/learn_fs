# File Research: sources/os/plan9/9front/sys/src/cmd/kc/sgen.c

Addressability and complexity analysis for backend expression trees. `xcom` computes `addable` classes and register complexity, rewrites multiply/divide/modulo by powers of two into shifts/masks, normalizes immediate operands to the right side for commutative and comparison operations, and marks function calls as high-complexity barriers.

The comments define the compact addressability lattice used by `cgen`: constants, names, registers, indirect registers, address-of combinations, and constant-offset additions. After local rewrites, it invokes `com64` for 64-bit transformations. This file feeds evaluation-order decisions and direct-address emission in later codegen phases.
