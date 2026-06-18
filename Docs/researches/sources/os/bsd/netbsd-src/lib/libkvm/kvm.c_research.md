# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm.c

Implements core `libkvm` descriptor management, open/close, namelist lookup, crash dump header parsing/writing, and `kvm_read`/`kvm_write`.

Key behavior:
- `_kvm_open()` initializes `kvm_t`, selects kernel namelist (`/dev/ksyms` or kernel file), opens physical memory/dump, optionally opens `/dev/kmem` and swap, and initializes machine-dependent translation for crash dumps.
- `_kvm_get_header()` parses savecore-style `kcore` headers with CPU and memory segments.
- `kvm_dump_mkheader()` handles raw dump-device format and constructs an in-memory `kcore_hdr`.
- `kvm_dump_header()` writes generic, CPU, and data segment headers through a callback.
- `_kvm_pread()` supports mmap-backed dumps and aligned-buffer reads for devices requiring block alignment.
- `kvm_read()` routes live-kernel reads through `/dev/kmem`, rejects reads for `KVM_NO_FILES`, and walks dead-kernel virtual addresses via `_kvm_kvatop()`/`_kvm_pa2off()`.

This is the central architecture-neutral layer that all machine-dependent translation modules serve.
