# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/l.s

## Purpose
Non-startup x86 assembly support for the protected-mode boot kernel: paging-off handoff, BIOS32 calls, CPU/system-register helpers, atomics, trap entry stubs, interrupt vectors, and SPL primitives.

## Main Interfaces
- Exports `pagingoff`, `bios32call`, `cgapost2`, `ltr`, `invlpg`, `wbinvd`, `lcycles`, `cpuid`, `fpoff`, `fpinit`, `tas`, `_xinc`, `_xdec`, `xchgw`, `cmpswap486`, `mul64fract`, `gotolabel`, `setlabel`, `halt`, `vectortable`, `forkret`, and many register/SPL helpers.
- Defines interrupt-vector call table entries for 0x00-0xFF.

## Implementation Notes
- `pagingoff` double-maps `KZERO` at physical 0, flushes CR3, switches to an identity-mapped path, disables paging, sets Multiboot registers, and jumps to the kernel entry.
- `bios32call` performs a far call through a BIOS32 pointer and copies register state in/out of `BIOS32ci`.
- `cpuid` first checks EFLAGS ID/AC toggling to distinguish 386/486/no-CPUID cases.
- FPU helpers manipulate CR0 EM/TS/NE bits and initialize x87 control word.
- Trap entry saves segment and general registers, switches DS/ES to kernel data selector, calls `trap`, then restores and `IRETL`s.
- `halt` only executes HLT when no runnable processes are ready.

## Dependencies And Risks
- Assembly offsets and vector-entry sizes are known by C trap setup.
- `pagingoff` depends on page-directory layout and Multiboot handoff conventions.
- Some instruction encodings are emitted manually for assembler compatibility.
