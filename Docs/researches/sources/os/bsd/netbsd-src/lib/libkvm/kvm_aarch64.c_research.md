# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_aarch64.c

Provides AArch64 machine-dependent crash dump address translation. It supports only dead-kernel translation and rejects live `vatop`.

Key behavior:
- Uses the AArch64 direct-map address range check before walking translation tables.
- Reads TCR/TTBR values from `cpu_kcore_hdr_t`.
- Derives page size from `TCR_TG1`, computes page-table levels from `TCR_T1SZ`, and walks TTBR1 tables until a block or page entry is found.
- `_kvm_pa2off()` maps physical addresses to packed dump offsets by walking `kh_ramsegs`.

`_kvm_mdopen()` sets user VA bounds from `VM_MIN_ADDRESS` and `VM_MAXUSER_ADDRESS`.
