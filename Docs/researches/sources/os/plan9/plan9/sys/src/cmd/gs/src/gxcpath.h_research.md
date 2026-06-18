# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcpath.h

## Purpose
Exposes clipping list and clipping device implementation details needed by stack-allocated clipping clients and lower-level clipping code.

## Public Surface
- `gx_clip_rect`: linked rectangle with integer bounds and `to_visit` enumeration bookkeeping.
- `gx_clip_list`: either a single rectangle or a linked list with dummy head/tail entries, aggregate x bounds, and rectangle count.
- `gx_device_clip`: forwarding clipping device containing a clip list, current rectangle cursor, translation, cached clipping box, and target forwarding state.
- Device constructors: `gx_make_clip_translate_device`, `gx_make_clip_device`, `gx_make_clip_path_device`.
- Clip-list helpers exported from `gxcpath.c`: `gx_clip_list_init`, `gx_clip_list_free`, `gx_cpath_set_outer_box`, `gx_cpath_list`.

## Semantics
- Clip lists are ordered by Y ranges; consecutive rectangles either share Y bounds or start at/after the previous rectangle's bottom.
- A list with `count <= 1` is considered rectangular.
- Clipping devices cache their clipping box, so their target clipping box and clip list must remain unchanged after open.

## Dependencies
Requires Ghostscript device forwarding structures and clipping path declarations from included context.

## Risks and Notes
- The header intentionally exposes implementation structures, so external users must honor invariants usually hidden behind higher-level APIs.
- Translation-aware clipping devices are documented as late additions used mainly for split transfers.

Filesystem relevance: none. This is clipping device metadata.
