# File Research: sources/os/bsd/dragonflybsd/sys/sys/assym.h

Read completely: 52 lines.

This kernel-only header defines macros for exporting C constants to assembly generation.

Key contents:
- Rejects inclusion outside `_KERNEL` or `_KERNEL_STRUCTURES`.
- `ASSYM_BIAS` avoids zero-sized arrays.
- `ASSYM_ABS()` handles negative values without simple signed overflow.
- `ASSYM(name, value)` emits several char arrays encoding sign and 16-bit chunks of the absolute value in their sizes.

Security/reliability notes:
- This is build-time metaprogramming, not runtime logic.
- Correctness depends on consumers interpreting generated symbol sizes consistently.
