# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrppm.c

IJG `djpeg` destination adapter for raw PPM/PGM output, compiled only under `PPM_SUPPORTED`.

Key behavior:

- Emits raw P5 PGM for grayscale and raw P6 PPM for RGB.
- Supports standard 8-bit byte samples and optionally nonstandard 2-byte-per-sample output for wider `JSAMPLE` builds unless `PPM_NORAWWORD` downscaling is selected.
- Uses direct `JFWRITE()` from the decompressor row buffer in the common case where `JSAMPLE` is byte-sized and no quantized colormap demapping is needed.
- Uses `copy_pixel_rows()` for sample-size translation, `put_demapped_rgb()` for quantized RGB indexes, and `put_demapped_gray()` for quantized grayscale indexes.

`jinit_write_ppm()` calculates output dimensions, allocates a physical I/O buffer, decides whether the decompressor can write directly into it, and installs the appropriate row callback. `finish_output_ppm()` only flushes and checks the stream.
