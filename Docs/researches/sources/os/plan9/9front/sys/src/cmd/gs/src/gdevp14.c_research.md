# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevp14.c

## Purpose

`gdevp14.c` implements Ghostscript's PDF 1.4 transparency compositing device. It provides in-memory planar buffers for PDF transparency groups and masks, composes them with Ghostscript blend routines, and acts as a compositor/filter device around a target output device. It also includes clist-specific support so banded rendering can record PDF 1.4 transparency operations during command-list writing and replay/compose them during command-list reading.

## Main Structures and Devices

The file defines GC descriptors for `pdf14_buf`, `pdf14_ctx`, `pdf14_device`, and an internal `pdf14_clist_device`. `pdf14_buf` instances are stack frames for rendered transparency groups: planar color components, alpha, optional shape, optional group alpha, bounding box, transfer function pointer, and links to saved buffers. `pdf14_ctx` owns the active stack, optional mask buffer, memory allocator, overall rectangle, additive/subtractive polarity flag, and channel count.

Three main prototype devices are exported: `gs_pdf14_Gray_device`, `gs_pdf14_RGB_device`, and `gs_pdf14_CMYK_device`. They share `pdf14_procs` but differ in color model and mapping procs. The clist side similarly defines gray/RGB/CMYK `pdf14_clist_*` prototypes for banded output.

## Control Flow

Opening the device (`pdf14_open`) allocates a base `pdf14_ctx` over the page rectangle with color components plus alpha. Transparency group begin/end calls convert user-space bounding boxes into device rectangles, push a new `pdf14_buf`, then later pop and composite it into the previous stack buffer. Mask begin/end pushes a mask buffer with background alpha and transfer function, then stores it in `ctx->maskbuf` for the next group composite.

The core pixel compositing happens in `pdf14_pop_transparency_group`. It iterates each pixel in the popped group's rectangle, reads source and destination planar values, optionally applies a transparency mask, handles additive vs subtractive component polarity, and dispatches to `art_pdf_composite_knockout_isolated_8`, `art_pdf_composite_group_8`, or `art_pdf_recomposite_group_8` depending on knockout/isolation state. It also updates destination shape and group alpha planes.

Marks arrive largely through high-level Ghostscript paths/images/text. `pdf14_fill_path`, `pdf14_stroke_path`, `pdf14_begin_typed_image`, and `pdf14_text_begin` capture current opacity, shape, and blend mode from the imager state. Rectangle fills route to `pdf14_mark_fill_rectangle` or `pdf14_mark_fill_rectangle_ko_simple`, which do per-pixel alpha/blend updates into the active planar buffer.

When the PDF 1.4 compositor is popped, `pdf14_put_image` emits the composed buffer to the target device as a normal image, flattening alpha over a solid white or black background depending on color polarity.

## Compositor and Clist Integration

`gs_pdf14_device_push` creates a matching PDF 1.4 device for the target's default blend space and overrides the imager state's color map procs so transfer functions are not applied before blending. `gx_update_pdf14_compositor` handles PDF14 operations such as push/pop device, begin/end group, begin/end mask, and blend-parameter updates.

Compositor objects are serialized for clist use by `c_pdf14trans_write` and reconstructed by `c_pdf14trans_read`. The code stores compact opcodes and operation-specific fields, including group isolation/knockout, opacity/shape, mask background, transfer function data, and changed blend parameters.

The clist writer side (`pdf14_clist_device`) exists because banded rendering needs a color model matching the PDF 1.4 blending space while the actual compositing is deferred. `pdf14_clist_create_compositor`, `pdf14_clist_update_params`, and the clist fill/stroke/text/image wrappers ensure blend state changes are sent through the command list before marks whose low-level rendering routines cannot see the full imager state.

## Dependencies

This file depends on Ghostscript device, graphics-state, image, clipping, color-map, clist, and transparency APIs, plus PDF blend functions from `gxblend.h`. Its public declarations are in `gdevp14.h`. It conditionally includes libpng-style support behind `DUMP_TO_PNG` for debugging dumps.

## Filesystem Relevance

There is no filesystem implementation here. File I/O is indirect through target devices and command-list infrastructure. Its relevance to the repository is as a Plan 9-hosted Ghostscript source file in the OS source tree.

## Risks and Notes

The code is memory- and integer-sensitive: planar buffer sizing computes `rowstride * height * planes`, with an explicit double-to-`max_uint` guard, but many later loops assume rectangles and channel counts are valid. A notable correctness comment says non-isolated knockout groups are forced isolated as a hack, so strict PDF transparency semantics are not fully implemented. The compositor serialization uses raw `memcpy` of structs and floats into clist byte streams, coupling it to the producer/consumer build ABI. Transfer functions and mask buffers are manually allocated/freed and require careful GC descriptors.
