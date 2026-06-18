# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/bpf-ipf.h

## Purpose
Local BPF compatibility header for IPFilter.

## Main Elements
- Defines BPF version, alignment, buffer limits, ioctls, `bpf_program`, `bpf_stat`, `bpf_version`, and `bpf_hdr` when system BPF definitions are absent.
- Defines many `DLT_*` link-layer type constants.
- Defines BPF instruction classes, modes, ALU/JMP operations, source/rval helpers, `struct bpf_insn`, and initializer macros.
- Declares `bpf_validate()` and `bpf_filter()`.

## Dependencies And Integration
Used by `bpf_filter.c` and the IPF BPF rule parser path to provide a stable BPF instruction ABI independent of host headers.

## Risk Notes
Local BPF copies can diverge from platform BPF/libpcap definitions. The header is guarded by `BPF_MAJOR_VERSION` to avoid duplicate definitions.
