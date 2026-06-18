# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_i386pae.c

Provides the PAE-specific i386 KVA translator used by `kvm_i386.c`. It compiles with `#define PAE`, reads PAE-format PDE/PTE entries, ignores the per-CPU L3 page for kernel VA translation, supports 2MB large pages, and validates present bits before returning a physical address.

It depends on `_kvm_pa2off()` from the main i386 module for reading page-table entries from dumps.
