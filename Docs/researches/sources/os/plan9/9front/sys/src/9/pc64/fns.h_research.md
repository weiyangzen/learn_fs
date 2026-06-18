# File Research: sources/os/plan9/9front/sys/src/9/pc64/fns.h

Architecture-specific function prototype header for the PC64 kernel.

Key contents:
- Includes shared `portfns.h`, then declares PC64 functions and assembly entry points.
- Covers architecture initialization, boot arguments, CPU identification, clocks, DMA stubs, FPU lifecycle, control/debug register access, I/O port primitives, interrupt/trap entry, MMU mapping, MTRR/PAT, PCI/PCMCIA hooks, process save/restore, real-mode calls, random generation, screen setup, syscall entry, VMX helpers, VM mapping, and reboot/config functions.
- Defines no-op or direct macros for x86-specific behavior: `dmaflush`, `evenaddr`, `kmapinval`, `mmuflushtlb`, `userureg`, `KADDR`, and `PADDR`.
- Declares external function-pointer hooks such as `cycles`, `coherence`, `screenputs`, PCI config accessors, and processor context callbacks.

Notable dependencies:
- Types from `dat.h`, `mem.h`, and shared port headers.

Research notes:
- This is the bridge between C code and the assembly implementations in `l.s`.
- The header centralizes many platform service contracts, so changing prototypes here has broad kernel impact.
