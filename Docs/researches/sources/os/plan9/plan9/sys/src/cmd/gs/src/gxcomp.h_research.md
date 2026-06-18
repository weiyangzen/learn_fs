# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcomp.h

## Purpose
Defines the internal compositor type model used by Ghostscript devices and command lists.

## Public Surface
- Compositor ids: `GX_COMPOSITOR_ALPHA`, `GX_COMPOSITOR_OVERPRINT`, `GX_COMPOSITOR_PDF14_TRANS`.
- `gs_composite_type_procs_t`: method table for default compositor creation, equality, command-list serialization/deserialization, clist writer update, and clist reader update.
- `gs_composite_type_t`: compositor type descriptor with one-byte command-list id and procedure table.
- Default clist update hooks: `gx_default_composite_clist_write_update`, `gx_default_composite_clist_read_update`.
- `gs_composite_s`: reference-counted abstract compositor object with type, id, and rc header.
- `gs_composite_id(pcte)`: id accessor macro.

## Semantics
- Command lists cannot serialize raw type-table addresses, so each compositor type needs a stable one-byte id.
- `write` and `read` procedures are responsible for compact command-list representation of compositor instances.
- Clist update hooks allow compositors to adjust writer/reader devices when a compositor is pushed through banded rendering.

## Dependencies
Uses public compositor definitions from `gscompt.h`, Ghostscript reference counting, bit-format definitions, imager state, devices, and memory APIs.

## Risks and Notes
- The one-byte id space allows 255 compositor types, which the comment treats as sufficient.
- Compositor serialization correctness is critical for async/banded rendering because writer and reader may live in separate address spaces.

Filesystem relevance: none. It is compositing/rendering infrastructure.
