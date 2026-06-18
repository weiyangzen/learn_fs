# File Research: sources/os/plan9/plan9/sys/src/9/ppc/lblast.h

Assembly fragment defining a Blast-board `mmuinit0` routine for PowerPC BAT startup mapping.

Key responsibilities:
- Clears 64 TLB entries with `TLBIE`.
- Maps `KZERO` to physical 0 with BAT0 and BAT1, covering 512 MiB in two 256 MiB regions.
- Maps `FPGABASE` uncached through DBAT2.
- Maps `INTMEM` direct/uncached through DBAT3.
- Leaves IBAT2 and IBAT3 unused.
- Enables IR/DR/RI/FP in MSR and returns through `RFI` into virtual mode.

Dependencies:
- Uses constants and macros from `mem.h` and the PPC assembler environment.
- Duplicates the non-`ucuconf` path now present directly in `l.s`.

Notable risks:
- Appears to be a legacy or include-style startup fragment; if included with `l.s`, duplicate `mmuinit0` definitions would conflict.
- Hard-coded BAT layout assumes Blast/MPC8260 board memory map.
