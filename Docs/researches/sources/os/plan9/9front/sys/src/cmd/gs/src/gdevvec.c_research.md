# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvec.c

## Purpose
Shared utility implementation for Ghostscript vector-style devices such as PDF, PostScript, PCL XL, CGM, metafile, and similar high-level output formats.

## Main Concepts
- Provides default vector procedure implementations for paths, rectangles, polygons, clipping, output files, image enumeration, and common shape fills.
- Caches device graphics state so concrete vector devices only emit changes.
- Supports optional bounding-box tracking through a `gx_device_bbox`.
- Manages output file opening as seekable or sequential, plus stream buffering.

## Key Functions
- Path output:
  - `gdev_vector_dopath`
  - `gdev_vector_dorect`
  - `gdev_vector_dopath_init`
  - `gdev_vector_dopath_segment`
  - `gdev_vector_write_polygon`
  - `gdev_vector_write_rectangle`
- State management:
  - `gdev_vector_init`
  - `gdev_vector_reset`
  - `gdev_vector_update_log_op`
  - `gdev_vector_update_fill_color`
  - `gdev_vector_prepare_fill`
  - `gdev_vector_prepare_stroke`
  - `gdev_vector_stroke_scaling`
- File/stream management:
  - `gdev_vector_open_file_options`
  - `gdev_vector_stream`
  - `gdev_vector_close_file`
  - `gdev_vector_get_params`
  - `gdev_vector_put_params`
- Clipping:
  - `gdev_vector_write_clip_path`
  - `gdev_vector_update_clip_path`
- Image enumeration:
  - `gdev_vector_begin_image`
  - `gdev_vector_end_image`
- Default device procs:
  - `gdev_vector_fill_rectangle`
  - `gdev_vector_fill_path`
  - `gdev_vector_stroke_path`
  - `gdev_vector_fill_trapezoid`
  - `gdev_vector_fill_parallelogram`
  - `gdev_vector_fill_triangle`

## Notable Behavior
- Optimizes rectangular paths and can merge collinear line segments.
- Defers fill-only isolated `moveto` operations to avoid an Acrobat Reader 4 artifact.
- Prevents changing `OutputFile` after output has begun unless safety and stream-position checks allow it.
- Uses a stream whose close procedure is changed to flush only, leaving final file closure to Ghostscript output-file handling.

## Notable Risks
- Some comments mark incomplete or wrong behavior, including fill padding value and initial saved color comments.
- `gdev_vector_stroke_path` computes a matrix for anisotropic stroke scaling but passes `NULL` to `dopath`, so the intended inverse path transform is not applied in that call.
- Many default operations fall back to raster/default behavior on errors, which may surprise concrete vector devices expecting purely high-level output.
- Output-file changes require careful state handling because vector formats typically write headers early.

## Filesystem Relevance
Manages output files and buffered streams for vector devices. It is output infrastructure, not filesystem implementation code.
