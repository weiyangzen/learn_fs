# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k_cmn.c

Common m68k translation implementation. It chooses 68030-style or 68040/68060-style MMU walkers from kcore MMU type and exports `_kvm_ops_cmn`.

Key behavior:
- `_kvm_cmn_kvatop()` rejects live kernels, selects `vatop_030` or `vatop_040`, and starts from `sysseg_pa`.
- Both walkers special-case early relocation ranges before full translation is available.
- `vatop_030()` reads segment table and page table entries using m68k kcore masks.
- `vatop_040()` walks three descriptor levels before reading a PTE.
- `_kvm_cmn_pa2off()` maps physical addresses through fixed m68k RAM segment arrays.

The implementation avoids machine-specific headers beyond m68k common headers so it can build across all m68k machines.
