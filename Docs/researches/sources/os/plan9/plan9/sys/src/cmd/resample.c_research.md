# File Research: sources/os/plan9/plan9/sys/src/cmd/resample.c

Read status: complete, 327 lines.

`resample` is an image resizing command for Plan 9 image files. It reads a `Memimage`, computes requested width/height from absolute values or percentages, resamples with a Kaiser-windowed kernel, and writes the result.

`i0` approximates the modified Bessel function used by `kaiser`; `main` precomputes and normalizes the kernel. `resamplex` and `resampley` resize in separable passes across byte-per-channel scan lines. Unsupported compact formats are converted to RGB24 or GREY8, resampled, and converted back.

Filesystem relevance: ordinary image file I/O through `readmemimage` and `writememimage`; not a filesystem component.
