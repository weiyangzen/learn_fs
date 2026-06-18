# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtmap.h

Defines Ghostscript transfer/mapping procedure types.

Key contents:
- Forward-declares abstract `gx_transfer_map`.
- Defines legacy `gs_mapping_proc`, which maps one float value with a transfer-map argument.
- Defines closure-style `gs_mapping_closure_proc_t`, which additionally receives caller-owned procedure data.
- Defines `gs_mapping_closure_t` holding a procedure pointer and data pointer.

Dependencies:
- Uses common Ghostscript scalar types such as `floatp`.

Research notes:
- The same mapping abstraction is used for transfer functions, black generation, and undercolor removal.
- Comments note that `gx_transfer_map` is broader than the name suggests and should probably be renamed to a mapping cache.
