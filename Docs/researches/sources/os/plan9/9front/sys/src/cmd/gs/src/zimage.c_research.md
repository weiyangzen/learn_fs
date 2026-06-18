# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage.c

## Purpose
Implements Level 1/2 image and imagemask operator setup plus common image data-source processing.

## Key Functions
- `data_image_params()` parses common image dictionary fields and DataSource operands.
- `pixel_image_params()` adds current color-space handling and pixel-image options.
- `zimage_setup()` starts a typed image and delegates source handling.
- `image1_setup()`, `zimage1()`, and `zimagemask1()` create standard image and mask image paths.
- `zimage_data_setup()` stores data sources and initializes an image enumerator.
- `image_proc_process()` / `image_proc_continue()` handle procedure data sources.
- `image_file_continue()` handles file data sources and stream read exceptions.
- `image_string_continue()` handles string data sources.
- `image_cleanup()` releases image enumerators.

## Important Behavior
- Supports procedure, string, and Level 2 file data sources, with all sources required to be the same type.
- Tracks identical file-source aliasing so shared stream buffers are consumed correctly.
- Procedure sources support `e_RemapColor` callbacks and resume through execution-stack continuations.
- Image enumerators are allocated in local memory to avoid global/local VM ownership problems.
- Empty images clean up immediately and pop operands.

## Research Notes
Critical image interpreter machinery coordinating PostScript data sources, streams, VM, graphics state, and image rendering.
