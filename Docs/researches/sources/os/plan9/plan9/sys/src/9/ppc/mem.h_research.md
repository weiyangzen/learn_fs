# File Research: sources/os/plan9/plan9/sys/src/9/ppc/mem.h

Shared PPC memory, register, MMU, trap, and address-layout constants for C and assembly.

Key contents:
- Selects `ucu.h` or `blast.h` depending on `ucuconf`.
- Defines byte/page/cache sizes, PTE/PTEG sizes, `MAXMACH`, `MACHSIZE`, `KSTACK`, and clock tick rate.
- Defines PowerPC SPR numbers, BAT register macros, MSR bit encodings, SRR1 TLB bits, exception vector codes, and special register assignments for `m` and `up`.
- Defines hashed-page-table and segment-map constants, PTE0/PTE1 encoding helpers, WIMG/PP bits, and HID0 cache bits.
- Defines virtual layout: `KZERO=0x80000000`, `KTZERO=0x80100000`, user text/stack top, `UREGSIZE`, `MACHADDR`, and `MACHPADDR`.
- Defines MPC internal memory and IO base constants plus `getpgcolor`.

Role:
- Forms the low-level ABI shared by `l.s`, trap handling, MMU code, mainline initialization, and hardware drivers.

Notable risks:
- Many assembly offsets and masks depend directly on these constants.
- `isphys(x)` uses the `KZERO` bit convention for this kernel layout.
- The selected board header radically changes memory sizes and PTE policy.
