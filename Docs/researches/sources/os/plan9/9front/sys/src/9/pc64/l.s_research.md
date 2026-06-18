# File Research: sources/os/plan9/9front/sys/src/9/pc64/l.s

Core amd64 assembly for kernel bootstrap, CPU control, low-level I/O, synchronization, FPU instructions, random instructions, VMX instructions, syscall/trap entry, and interrupt vectors.

Key behavior:
- Boot path starts in 32-bit mode, handles multiboot entry, builds initial identity and high-half mappings, enables long mode, jumps to virtual 64-bit kernel space, clears BSS, initializes `m`, and calls `main`.
- Defines bootstrap GDT descriptors and GDT pointer records for protected and long mode.
- Implements port I/O helpers (`inb`, `ins`, `inl`, `outb`, `outs`, etc.), descriptor table loads, task register load, control register access, XCR access, MSR read/write, cache/TLB instructions, memory fences, and timestamp counter read.
- Implements interrupt priority helpers `splhi`, `spllo`, `splx`, `islo`, atomic test-and-set, compare-and-swap, and scheduler label save/restore.
- Provides FPU/SIMD instruction wrappers used by `fpu.c`.
- Provides RDRAND helpers and buffer filling.
- Provides debug-register and VMX instruction wrappers with shared error-return paths.
- Implements transition to user mode, syscall entry, fork return, interrupt common entry, note return, and interrupt restore.
- Generates the interrupt vector table stubs used by `trapinit0`.

Notable dependencies:
- Register conventions from `mem.h`, especially `RMACH` and `RUSER`.
- C trap/syscall handlers and kernel globals such as `m`, `up`, `main`, `trap`, `syscall`, and `noteret`.

Research notes:
- Several fault-sensitive instruction wrappers expose labels (`_rdmsrinst`, `_wrmsrinst`, `_peekinst`) that `trap.c` recognizes to recover from expected faults.
- This file is central to ABI correctness: stack layout and saved register order must match `Ureg` and syscall/trap C code.
