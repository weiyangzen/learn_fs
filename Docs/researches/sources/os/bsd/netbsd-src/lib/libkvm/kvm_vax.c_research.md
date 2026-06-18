# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_vax.c

VAX libkvm crash-dump support, explicitly described as a minimal/error-prone stub. Initialization allocates `vmstate`, resolves kernel `_end`, and translation accepts only `[KERNBASE, end)` as a direct kernel-to-physical offset.

`_kvm_pa2off()` is direct despite a note that crash dumps may not work. `_kvm_mdopen()` sets VM user address limits.
