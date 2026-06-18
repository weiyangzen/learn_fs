# File Research: sources/os/plan9/9front/sys/src/9/pc/fns.h

Declares the PC architecture function surface for the 9front kernel, after including shared port-layer declarations from `../port/portfns.h`.

Key elements:
- Covers architecture setup and reset: `archinit()`, `archreset()`, `mach0init()`, `trapinit()`, `trapinit0()`, `links()`, `meminit()`, `mmuinit()`, and related boot/memory configuration helpers.
- Declares BIOS32 helpers, real-mode entry, NVRAM access, ACPI/RSD search helpers, and configuration/environment routines.
- Declares CPU identification, CPUID access, cycle counters, delay loops, TSC/i8253 timer routines, MTRR/PAT support, cache/memory barriers, and random buffer generation.
- Declares FPU process lifecycle routines: `fpuinit()`, `fpuprocsetup()`, `fpuprocfork()`, `fpuprocsave()`, `fpuprocrestore()`, plus low-level FP save/restore hooks.
- Declares x86 control/debug register accessors and mutators: CR0-CR4, XCR0, DR registers, TLB flush macro, GDT/IDT/LDT/TSS loaders, and page invalidation.
- Declares DMA, ISA config, PCI config, PCMCIA mapping/special matching, I/O port input/output, interrupt/trap enable/disable, and memory mapping functions.
- Declares console/screen initialization, keyboard/controller routines, serial console allocation, i8253 timer routines, and process context hooks.
- Provides PC-specific macros: `userureg()`, `KADDR()`, `PADDR()`, `dmaflush()`, `evenaddr()`, and `kmapinval()`.
- Many declarations are function pointers selected at runtime, such as `cmpswap`, `coherence`, `cycles`, `fpsave`, `fprestore`, and PCI config accessors.

Filesystem relevance: indirect. This header is central architecture glue used by storage, filesystem, network, and driver code throughout the PC kernel because it exposes low-level I/O, DMA, interrupts, memory mapping, and process context operations.
