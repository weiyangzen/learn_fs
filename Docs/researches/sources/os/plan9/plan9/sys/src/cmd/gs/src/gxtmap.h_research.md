# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtmap.h

Small shared header defining Ghostscript transfer/mapping function callback types.

Key contents:
- Forward-declares abstract `gx_transfer_map`.
- Defines legacy `gs_mapping_proc`, taking a value and transfer map.
- Defines closure-style `gs_mapping_closure_proc_t`, taking value, transfer map, and caller data.
- Defines `gs_mapping_closure_t` with a procedure pointer and opaque data pointer.

Research notes:
- The same mapping abstraction is used for transfer functions, black generation, and undercolor removal.
- The comment notes that `gx_transfer_map` should probably be renamed to a more general mapping cache.
