# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgc.h

## Role

`gsgc.h` declares the library-level interface to Ghostscript VM spaces and garbage collection.

This is memory-management infrastructure, not filesystem code.

## Main Definitions

- `i_vm_space`
  - `i_vm_foreign`
  - `i_vm_system`
  - `i_vm_global`
  - `i_vm_local`
- `vm_spaces`
- `vm_reclaim_proc`
- convenience aliases:
  - `space_foreign`
  - `space_system`
  - `space_global`
  - `space_local`
  - `spaces_indexed`
- `GS_RECLAIM`
- backward-compatible `gs_reclaim`

## Important Semantics

VM spaces are ordered by dynamism. Pointers from more dynamic spaces to equal or less dynamic spaces are allowed, but not the reverse. Foreign space is index 0 so scalar refs need no space bits.

## Notable Risks

The header leaks interpreter-level concepts such as `gs_ref_memory_t` and the four PostScript memory spaces into the library layer, which it acknowledges in its opening comment.
