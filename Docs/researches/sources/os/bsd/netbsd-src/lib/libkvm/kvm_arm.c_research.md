# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_arm.c

Implements ARM32 machine-dependent KVA translation for crash dumps. It validates CPU kcore version/flags, selects kernel or user L1 table based on virtual address, reads L1 descriptors, and handles section, coarse, and fine page-table paths.

Supported mappings:
- L1 section mappings.
- L2 large, small, and tiny page mappings.

`_kvm_pa2off()` maps physical addresses through ARM kcore RAM segments. `_kvm_mdopen()` derives user-space maximum from `__ps_strings + 1` because ARM VM limits vary across machines.
