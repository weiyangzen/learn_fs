# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcolor2.h

## Purpose
Defines internal Level 2 color support structures for cached Indexed/Separation color transforms and uncolored tiling pattern instances.

## Public Surface
- `gs_indexed_map`: reference-counted cache for indexed lookup or separation tint-transform results, including procedure union, `proc_data`, value count, and float values.
- `lookup_indexed_map(...)`: lookup procedure that returns cached map values.
- `alloc_indexed_map(...)`: allocates a map and its value storage.
- `free_indexed_map(...)`: reference-count free procedure.
- `gs_pattern1_instance_t`: internal representation of a Type 1 pattern instance with template, step matrix, tiling bbox, simplicity flag, mask flag, device size, and bitmap id.

## Dependencies
Includes Level 2 color public declarations, matrices, reference counting, and bitmap ids. Structure descriptors are implemented in related color/pattern source files.

## Risks and Notes
- `gs_indexed_map.values` is described as a flexible logical array but is stored as a pointer, so allocation and reference-count management must stay paired.
- Pattern instance comments document adjusted tiling-space semantics used to simplify repeated tile coverage calculations.

Filesystem relevance: none. This is color/pattern rendering metadata.
