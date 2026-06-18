# File Research: sources/os/plan9/plan9/sys/src/9/ppc/l.s

PowerPC assembly support for early boot, BAT/MMU enablement, trap entry/return, TLB miss fast paths, atomic operations, cache maintenance, FPU state, and SPR accessors.

Key responsibilities:
- `start` disables interrupts, sets `SB`, enters `mmuinit0`, builds `Mach`, zeroes `up`, and calls C `main`.
- `mmuinit0` clears TLBs, programs BAT mappings for kernel DRAM, FPGA/IO, and direct internal-memory access, then enables instruction/data translation via `RFI`.
- Implements interrupt priority primitives: `splhi`, `splx`, `spllo`, `islo`.
- Provides process transition helpers: `touser`, `setlabel`, `gotolabel`, `forkret`.
- Implements exception vector save/restore: `tlbvec`, `trapvec`, `saveureg`, and `restoreureg`.
- Implements 603e-style instruction/data TLB miss handlers `imiss` and `dmiss` that search hash PTE groups before falling back to normal trap handling.
- Provides TLB/cache primitives: `tlbflushall`, `tlbflush`, `dczap`, `dcflush`, `icflush`, cache enable/disable helpers, and `mmudisable`.
- Provides atomic helpers: `tas`, `_xinc`, `_xdec`, `cmpswap`.
- Saves/restores all 32 FPU registers plus FPSCR and initializes Plan 9 FP constants.
- Exposes many SPR accessors for MSR, BAT, HID, SDR1, segment registers, hash registers, miss registers, DEC, DAR, DSISR, and related PowerPC state.
- Includes `ucuconf`-specific PPC 755/L2 cache/BAT helpers and `mul64fract`.

Important behavior:
- Uses `SPRG0..3` to preserve R0/R1/LR/vector across low-level exception entry.
- Trap entry detects user versus kernel mode and switches user traps onto the current process kernel stack.
- `saveureg` re-enables MMU translation before returning to C trap handlers.
- TLB miss fast paths count `m->tlbfault`, `m->imiss`, and `m->dmiss`.
- Atomic operations use load-reserve/store-conditional and include `DCBF` workarounds for 603x issues.
- `mmudisable` also disables I/D caches before returning to a physical caller.

Dependencies:
- Must match `mem.h` constants, `Ureg` layout, `Mach` field offsets, PowerPC assembler conventions, and C trap/syscall/MMU code.
- Calls C symbols such as `main`, `trap`, and cache/MMU helpers.

Notable risks:
- Any mismatch between `Ureg` offsets here and C trap structures breaks all exception return.
- BAT constants are board-configuration-sensitive and differ under `ucuconf`.
- TLB miss code assumes hash table layout and PTE group format used by `mmu.c`.
- The file mixes generic PPC, MPC8260, and UCU/Saturn-specific paths behind preprocessor conditionals.
