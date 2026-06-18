# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdctd.c

Implementation of Ghostscript’s `DCTDecode` JPEG stream filter.

Core behavior:

- Installs IJG source-manager callbacks for initialization, buffer refill, skipping input data, resync, and termination.
- `dctd_fill_input_buffer` suspends when more input is needed, or injects a fake EOI marker at final input EOF.
- `dctd_skip_input_data` tracks skipped bytes across caller buffers.
- `s_DCTD_process` runs a phase machine:
  - Skip leading garbage before the JPEG marker.
  - Read JPEG headers.
  - Apply `ColorTransform` if supplied and not overridden by an Adobe marker.
  - Start decompression.
  - Allocate an oversized scanline buffer if output scanlines exceed template output size.
  - Read scanlines into caller output or the intermediate buffer.
  - Finish decompression and return `EOFC`.
- `s_DCTD_release` destroys JPEG state, frees scanline buffer and decompression data, and restores the stream template pointer.

This is JPEG decompression stream code, not filesystem logic.
