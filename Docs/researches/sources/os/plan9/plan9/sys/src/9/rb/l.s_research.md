# File Research: sources/os/plan9/plan9/sys/src/9/rb/l.s

MIPS 24K RouterBOARD low-level assembly for boot, traps, software TLB, cache, atomics, and CP0 access.

Key responsibilities:
- `start` initializes `R30`, disables interrupts, validates data-segment alignment, clears compare/status/cause, disables watchdog action, cleans cache, configures KSEG0 caching, initializes `Mach`, clears BSS, and calls `main`.
- `touser` enters user mode at `UTZERO+32`.
- Implements interrupt priority helpers: `intron`, `introff`, `idle`, `wait`, `splhi`, `splx`, `spllo`, `islo`.
- Provides context helpers `setlabel`/`gotolabel`.
- Implements TLB operations: `puttlb`, `puttlbx`, `gettlbx`, `gettlbp`, `gettlbvirt`, wired/page-mask/random helpers.
- Implements software-TLB hash lookup in the UTLB miss vector, filling hardware TLB directly on cache hits or falling back to full exception handling.
- Provides exception vectors and `exception` entry handling for user/kernel traps and syscalls.
- Saves/restores `Ureg` frames, implements `forkret`, and handles kernel `wait` PC advancement.
- Implements atomics `tas`, `_xinc`, `_xdec`, `cmpswap`.
- Implements `icflush`, `dcflush`, `cleancache`.
- Exposes CP0 status/count/compare/config/cause/watch/perf helpers and fake `C_fcr0`.

Important behavior:
- Software TLB hash macro must match C `mmu.c` calculations.
- Exception entry uses separate user and kernel stack paths.
- Syscall path calls C `syscall` and returns via `sysrestore`.
- Cache operations switch between cached/uncached execution with barrier macros.
- `C_fcr0` reports `0x500`, consistent with FP emulator/runtime expectations.

Dependencies:
- Must match `mem.h`, `mips.s`, `dat.h` `Mach` and `Ureg` offsets, and C trap/MMU/fault code.

Notable risks:
- Register save/restore order is a hard ABI with C.
- UTLB fast path correctness depends on software TLB hashing and ASID handling.
- Boot has a hard sanity check for data-segment alignment and returns to ROM if invalid.
