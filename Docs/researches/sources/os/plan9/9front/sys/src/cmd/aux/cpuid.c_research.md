# File Research: sources/os/plan9/9front/sys/src/cmd/aux/cpuid.c

Role: x86 CPUID inspection utility.

Core mechanism:
- Embeds raw x86 machine code bytes for CPUID in `_cpuid`, casts them to a function pointer, patches instruction bytes depending on detected 386/amd64 a.out header, then calls `segflush`.
- A note handler turns unsupported execution faults into `this information is classified`.

Output modes:
- Default decodes common leaves into named lines: vendor, processor model/family, features, extended features, processor name, physical/virtual address bits.
- `-r` prints raw leaves only.
- `-a` prints decoded leaves and raw unknown leaves.

Decoded leaves:
- Standard leaves 0, 1, 7, and 13.
- Extended leaves 0x80000001, 0x80000002-4 processor name, and 0x80000008 address sizes.

Notable issue:
- In `func1`, `model` is initially computed with the same shift/mask as family (`r.ax >> 8 & 0xf`), which looks suspicious because x86 model normally starts at bits 4..7.
