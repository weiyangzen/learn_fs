# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclist.h

## Purpose
Defines the main Ghostscript command-list data structures and public clist APIs.

## Main Responsibilities
- Documents the two-phase command-list model:
  - record drawing commands sorted by bands
  - replay commands band-by-band to render output
- Defines saved-page and placed-page structures.
- Defines tile cache structures used during write/read phases.
- Defines shared, writer, reader, and union forms of `gx_device_clist`.
- Provides initialization macro `clist_init_params`.
- Declares lifecycle and rendering APIs.

## Key Structures
- `gx_saved_page`: snapshot of a device plus band page metadata and copy count.
- `gx_placed_page`: saved page plus placement offset.
- `tile_hash`, `tile_slot`: bitmap/tile cache entries with per-band definition masks.
- `cmd_prefix`, `cmd_list`: buffered command-run list infrastructure.
- `gx_device_clist_writer`: write-phase state, including command buffer, band states, current imager state, tile cache state, retry policy, and disable mask.
- `gx_device_clist_reader`: read-phase state, including render plane and optional placed-page list.
- `gx_device_clist`: union over common/writer/reader views.

## Important Flags
`disable_mask` can disable specific clist behavior such as path fills, path strokes, high-level images, complex clips, pass-through params, and `copy_alpha`.

## Public APIs
- `clist_finish_page`
- `clist_close_output_file`
- `clist_close_page_info`
- `clist_compute_colors_used`
- `clist_setup_params`
- `clist_render_rectangle`

## Dependencies
Includes command-list I/O, banding, buffering, raster-plane, imager-state, and bitmap-cache headers.

## Research Notes
This header is the command-list contract. It is heavily stateful, and correctness depends on distinguishing fields valid in writer mode from fields valid in reader mode.
