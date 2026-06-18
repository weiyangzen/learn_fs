# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcfax.c

Ghostscript `cfax` output device that writes SFF format for CAPI fax devices.

Key responsibilities:
- Defines the `gs_cfax_device` fax printer device.
- Emits SFF document header, per-page header, encoded line records, page data, and document-end signature.
- Uses Ghostscript fax parameters via `gdev_fax_get_params` and `gdev_fax_put_params`.
- Encodes each scanline through a stream template, specifically CCITT fax encoding through `s_CFE_template`.
- Overrides close handling so multi-page SFF documents receive the required final document-end marker.

Important behavior:
- `cfax_print_page` initializes CCITT fax encoder state with byte alignment, low-order first bit order, no EOL/EOB, and `K = 0`.
- `cfax_begin_page` temporarily patches `pdev->width` to the fax-adjusted width when writing the SFF page header.
- `cfax_stream_print_page_width` encodes one line at a time, writing short or extended SFF block lengths depending on encoded byte count.
- If the output filename is `"nul"`, encoded data is computed but not written.

Dependencies:
- Ghostscript printer and fax infrastructure: `gdevprn.h`, `gdevfax.h`.
- Stream encoder infrastructure: `strimpl.h`, `scfx.h`.
- Uses `gdev_fax_init_fax_state`, `gdev_prn_copy_scan_lines`, stream template init/process/release callbacks, and Ghostscript memory allocators.

Notable risks:
- On encoder init failure inside the line loop, the function returns immediately without freeing allocated buffers.
- Output block buffer size is fixed at 1000 bytes; correctness depends on CCITT output for one row fitting this working model.
- Only SFF/CAPI-specific line block conventions are implemented; it is not a generic fax writer.
