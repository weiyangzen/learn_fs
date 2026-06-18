# File Research: sources/os/plan9/plan9/sys/src/9/pc/devarch.c

PC architecture device `#P`, I/O port allocator/accessor, CPU identification, architecture selection, and runtime architecture controls.

Key responsibilities:
- Maintains an I/O port allocation map with `ioinit`, `ioreserve`, `ioalloc`, `iofree`, and `iounused`.
- Implements `#P` files:
  - `ioalloc`
  - `iob`
  - `iow`
  - `iol`
  - dynamically added arch files.
- Provides `addarchfile()` for other code to extend `#P`.
- Allows raw I/O byte/word/long reads/writes after checking allocation conflicts, with VGA ranges exempted.
- Provides generic PC reset through i8042 reset and port `0xcf9`.
- Implements default `PCArch archgeneric`.
- Identifies CPU vendor/family/model via CPUID, selects CPU type names/timing constants, detects TSC/PSE/MCE/PGE/FXSR/SSE/SSE2, sets CR4 bits, calibrates CPU Hz, and selects FPU save routines.
- Exposes `cputype` and `archctl` files.
- `archctl` can toggle PGE, choose memory barrier implementation, enable/disable i8253 timer programming, and set MTRR cache ranges.
- Selects a concrete `PCArch` from `knownarch`, with fallback/default fields filled from `archgeneric`.
- Provides `pcmspecial` indirection, `fastticks`, microsecond conversion, and `timerset`.

Important behavior:
- Reserves a dummy I/O byte at `0x0fff` to support an IBM X20 boot quirk.
- `ioexclude` plan9.ini ranges are pre-allocated.
- Raw I/O access is denied for allocated ranges except VGA registers.
- Coherence defaults improve with CPU features: nop, `mb586`, or `mfence`.
- 386 systems switch to copy-on-reference mode and interrupt-disabled compare-and-swap.

Dependencies:
- Depends on x86 CPUID/MSR/CR helpers, i8259/i8253, MTRR code, Plan 9 devtab helpers, and known architecture list.

Notable risks:
- `#P/iob/iow/iol` are powerful privileged raw I/O interfaces.
- `archctl coherence nop` is only permitted on uniprocessors and is noted safe only under VMware.
- Some CPU type tables contain trial-and-error/guesswork timing constants.
