# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_powerpc.c

Implements 32-bit PowerPC machine-dependent crash dump translation.

Key behavior:
- Checks CPU PVR and supports several OEA-era PowerPC CPUs.
- Attempts BAT/direct block translations first, with separate 601 BAT handling.
- Falls back to segment register/hash page table translation via primary and secondary PTEG scans.
- `_kvm_pa2off()` maps physical addresses through kcore RAM segments.
- `_kvm_mdopen()` derives user VA range from `__ps_strings + 1` because limits vary across PowerPC machines.

Notable detail: secondary hash lookup calls `_kvm_scan_pteg()` with secondary flag `0`, matching the source as read; this is worth reviewing if investigating PowerPC translation misses.
