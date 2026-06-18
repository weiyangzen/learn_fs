# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun3x.c

Sun3x libkvm translator for crash dumps. It fast-paths addresses below `contig_end` as contiguous kernel physical memory, otherwise computes the kernel PTE address, reads it via `kvm_read`, validates `pg_valid`, and extracts the physical frame.

`_kvm_sun3x_pa2off()` walks `ram_segs` to convert sparse physical addresses to packed dump offsets.
