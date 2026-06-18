# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/bpf.h

## Purpose
`bpf.h` declares the BPF socket helper used by `dhcpleased`.

## Exports
- `BPFLEN`: fixed BPF read buffer length, set to `2048`.
- `get_bpf_sock(const char *)`: opens and configures a BPF descriptor for an interface.

## Integration Notes
Included by the main process and frontend packet code. `BPFLEN` also sizes frontend per-interface BPF receive buffers.
