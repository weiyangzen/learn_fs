# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsinit.c

Library initialization and finalization for the Ghostscript imager.

Functions:
- `gs_lib_init`: combines memory initialization and configured subsystem initialization.
- `gs_lib_init0`: creates the malloc-backed memory manager, resets debug flags, and clears error logging.
- `gs_lib_init1`: walks `gx_init_table` and invokes each configured init procedure.
- `gs_lib_finit`: calls platform cleanup via `gp_exit`.

Notable issue:
- `gs_lib_finit` comments that memory ownership is ambiguous: if `gs_lib_init0` allocated the memory, it should be released, but some API paths supply externally owned memory.
