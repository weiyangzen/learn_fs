# File Research: sources/os/plan9/9front/sys/src/9/zynq/mem.h

Purpose: Zynq ARM memory-layout, page-table, processor-state, and assembly macro definitions shared by C and assembly.

Key interfaces:
- Page/cache sizes, `MAXMACH`, `KSTACK`, `HZ`.
- Kernel/user virtual layout: `KZERO`, `KTZERO`, `VMAP`, `TMAP`, `KMAP`, `MACH`, `MACHL1`, `CONFADDR`, `USTKTOP`.
- PTE/L1/L2 constants and index macros.
- ARM CPSR mode bits and barrier/instruction macros.
- Register assignments `Rmach` and `Rup`.
- VFP register access macros and translation table attributes.

Integration notes: Included by all Zynq assembly and many C files.

Risk/attention points: This file is the contract for virtual memory layout and assembly constants; changes require coordinated updates across MMU, trap, and boot code.
