# File Research: sources/os/plan9/plan9/sys/src/9/rb/mem.h

RouterBoard MIPS memory, CPU, exception, TLB, and address-layout constants shared by C and assembly.

Key contents:
- Defines page sizes, stack sizes, cache sizes, cache-line size, alignment macros, and fixed single-CPU limits.
- Defines MIPS CP0 register numbers, status bits, config bits, cause bits, cache ECC bits, exception codes, and trap-vector addresses.
- Defines `Ureg` offsets and `UREGSIZE` for assembly trap-frame layout.
- Defines MIPS address segments (`KUSEG`, `KSEG0`, `KSEG1`, `KSEG2`, `KSEG3`), RouterBoard layout (`MACHADDR`, `KTZERO`, `REBOOTADDR`, `PHYSCONS`, `ROM`), and fixed `MEMSIZE`.
- Defines TLB page-size encodings, PTE bits, cacheability modes, soft-TLB sizing, ASID count, wired/random TLB boundaries, and user stack/text layout.

Role:
- This header is the ABI between low-level MIPS assembly, trap handling, MMU code, kmap, reboot code, and early console output.
- It encodes the MIPS 24K cache aliasing policy: 4 KiB pages use 8 colors, while larger pages collapse `NCOLOR` to 1.

Notable constraints:
- `PTECACHABILITY` is write-through (`PTENONCOHERWT`) because the comments cite MIPS 24K erratum 48 disallowing write-back.
- `NWTLB` is zero, so the wired large I/O TLB mechanism is compiled but unused.
- `MEMSIZE` is fixed at 256 MiB and `PCIMEM` is hard-coded for the rb450g platform.
