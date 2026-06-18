# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevifno.c

## Role
`gdevifno.c` implements the Ghostscript `inferno` device that emits compressed Inferno/Plan 9 bitmap image files.

## Device Definition
- Defines `inferno_device`, a printer-like device with `dither`, detected `ldepth`, previous `lastldepth`, and a flag tracking whether Ghostscript color-map callbacks occurred.
- The active `inferno_procs` currently use standard `gdev_prn_get_params`/`gdev_prn_put_params`; custom `Dither` get/put code exists but is commented out in the proc table.
- Default device is 100x100 DPI, 24-bit RGB, no margins.

## Color and Depth Detection
- `inferno_rgb2cmap` packs RGB bytes into a color index as blue:green:red and infers output `ldepth` from the colors Ghostscript requests:
  - black/white only can remain 0.
  - limited gray can raise to 1 or 2.
  - non-gray raises to 3.
- `inferno_cmap2rgb` reverses packed color indices and rejects values above 24 bits.
- `init_p9color` builds a 16x16x16 Plan 9 color-map dithering table at runtime.

## Print Path
- `inferno_print_page` allocates one Ghostscript scanline buffer, decides the output `ldepth`, opens a compressed image writer with `initwriteimage`, then converts each RGB scanline into Plan 9 packed pixels.
- For `ldepth == 3`, it always uses the `p9color` 2x2 dither matrix in the current code (`if(1 || dither)`).
- For `ldepth == 2` and `ldepth == 0`, it packs 4-bit and 1-bit pixels into bytes. `ldepth == 1` returns a fatal error.
- Each packed line is passed to `writeimageblock`; finalization is signaled with `nil, 0`.

## Compressed Image Writer
- Implements a modified Plan 9/Brazil `fb/bit2enc` compressor.
- `WImage` maintains an output block, sliding input window, dump buffer, rolling hash table, and hash chains.
- `gobbleline` finds repeated sequences with a 1024-byte window, emits raw dump runs or back-reference runs, and flushes block output as `"y n "` headers followed by compressed bytes.
- `writeimageblock` shifts the window, feeds complete lines to `gobbleline`, flushes at end-of-data, and writes the initial `"compressed"` image header through `initwriteimage`.
- Includes Plan 9 drawing-library helpers `bytesperline` and `rgb2cmap`; reverse `cmap2rgb` is present but commented out.

## Risks and Notes
- The custom `Dither` parameter functions contain `printf` debug output, but are not wired into the active procs.
- Several fatal paths return `gs_error_Fatal` rather than recoverable errors.
- This is the most Plan 9-specific file in the group. Its filesystem relevance is that it serializes a compressed bitmap file format to Ghostscript's output stream; it does not implement filesystem semantics.
