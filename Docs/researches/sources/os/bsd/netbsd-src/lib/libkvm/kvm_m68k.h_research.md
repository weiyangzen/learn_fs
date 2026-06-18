# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k.h

Defines the m68k operation-vector interface used by `kvm_m68k.c`. `struct kvm_ops` contains init/free/KVA-to-PA/PA-to-offset hooks. `struct vmstate` stores the selected ops, page-shift/mask fields, and a private pointer for lower layers.

Exports ops tables for common, generic 68k, sun2, sun3, and sun3x implementations.
