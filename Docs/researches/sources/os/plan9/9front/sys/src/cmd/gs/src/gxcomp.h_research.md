# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcomp.h

Compositor type and object definitions for Ghostscript compositing.

Key contents:
- Assigns one-byte command-list compositor IDs for alpha, overprint, and PDF 1.4 transparency compositors.
- Defines `gs_composite_type_procs_t` with hooks for default compositor creation, equality, command-list serialization/deserialization, clist write update, and clist read update.
- Defines `gs_composite_type_t` with compositor ID and proc table.
- Declares default clist write/read update implementations.
- Defines common reference-counted `gs_composite_t` object layout and `gs_composite_id`.

Notable dependencies:
- `gscompt.h`, reference counting, bit format definitions, `gx_device`, and `gs_imager_state`.

Research notes:
- The one-byte stable compositor ID exists because command lists may be replayed in a different address space where method-table pointers are meaningless.
- `gxclrast.c` uses this interface to deserialize and install compositors during clist playback.
