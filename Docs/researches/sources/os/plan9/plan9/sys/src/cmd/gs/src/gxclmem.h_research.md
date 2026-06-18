# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclmem.h

## Purpose
Declares structures and aliases for the memory-backed command-list file implementation.

## Main Responsibilities
- Defines block size `MEMFILE_DATA_SIZE`.
- Declares raw, physical, logical, and top-level memory-file structures.
- Defines GC descriptor macro for `MEMFILE`.
- Aliases `memfile_*` operations to generic `clist_*` I/O names.
- Declares compressor/decompressor prototype accessors.

## Key Structures
- `RAW_BUFFER`: doubly linked decompression cache block.
- `PHYS_MEMFILE_BLK`: allocated data block, raw or compressed.
- `LOG_MEMFILE_BLK`: logical block index entry pointing into physical storage.
- `MEMFILE`: state object for logical/physical file content, reserves, cursor position, stream state, and compression status.

## Important Design Notes
- Most helper structures are allocated on the C heap, while `MEMFILE` and stream states are GC-compatible.
- Reserve chains are part of the low-memory write guarantee used by command-list banding.
- `pdata` always points into raw bytes, whether original raw storage or decompressed cache storage.

## Dependencies
- `gxclio.h` for generic clist I/O interface.
- `strimpl.h` for stream state/cursor structures.

## Research Notes
This header exposes the full internal data model, so it is tightly coupled to `gxclmem.c`. The generic `clist_*` macro aliases let the same command-list code use memory-backed files transparently.
