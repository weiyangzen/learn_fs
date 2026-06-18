# File Research: sources/virtualization/qemu/block/parallels.h

## Purpose
Defines the shared Parallels image-format structures, constants, preallocation enum, driver state, and extension-reader prototype used by `parallels.c` and `parallels-ext.c`.

## Main Contents
- Geometry defaults: `HEADS_NUMBER`, `SEC_IN_CYL`, and `DEFAULT_CLUSTER_SIZE`.
- `ParallelsHeader`, the packed little-endian on-disk header with magic, version, geometry, BAT entry count, virtual sector count, in-use marker, data offset, flags, and extension offset.
- `ParallelsPreallocMode`, with `fallocate` and `truncate` modes.
- `BDRVParallelsState`, holding the coroutine lock, header/BAT pointers, dirty BAT bitmap, used-cluster bitmap, image extents, preallocation settings, geometry, offset multiplier, and migration blocker.
- `parallels_read_format_extension()` declaration.

## Dependencies
Includes QEMU coroutine declarations and expects block-layer types such as `BlockDriverState`, `Error`, and graph-lock annotations from surrounding includes.

## Filesystem/Block Relevance
This header is the data contract for Parallels sparse image metadata and runtime state. Its packed header layout defines the on-disk ABI used by the format driver.

## Risks and Notes
- `ParallelsHeader` is always little-endian; all users must convert fields explicitly.
- `BDRVParallelsState.lock` protects both BAT access and image extension, making it central to allocation correctness.
- Header changes are format changes and affect compatibility with Parallels/OpenVZ ploop-style images.
