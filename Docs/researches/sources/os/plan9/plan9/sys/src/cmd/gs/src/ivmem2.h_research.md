# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ivmem2.h

Purpose: declares VM control user-parameter setters exported by `zvmem2.c` for `zusparam.c`.

APIs:
- `set_vm_reclaim(i_ctx_t *, long)` updates VM reclaim policy.
- `set_vm_threshold(i_ctx_t *, long)` updates VM threshold behavior.

This is a small cross-module header for interpreter user-parameter plumbing.
