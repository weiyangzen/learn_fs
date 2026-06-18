# File Research: sources/os/plan9/9front/sys/src/9/kw/arm.s

Provides ARM assembly macros for early Kirkwood setup.

Key elements:
- Defines physical/virtual address conversion macros.
- Defines L1 page-table index and machine-address helpers.
- Defines page-table entry attributes for DRAM and I/O sections.
- Defines barrier macros for DMB, DSB, and ISB using CP15 operations.
- Defines `FILLPTE` and `ZEROPTE` macros for boot-time page-table construction.
- Provides a `WAVE` debug macro that writes a character to the physical console.

Dependencies:
- Includes `mem.h` and `arm.h`.
- Used by low-level assembly startup/exception code.

Research notes:
- The macros are tailored to ARM926EJ-S and Kirkwood cache/barrier behavior.
