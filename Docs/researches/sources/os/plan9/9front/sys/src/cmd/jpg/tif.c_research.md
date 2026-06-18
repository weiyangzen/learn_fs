# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/tif.c

Interactive TIFF viewer/converter command. It opens files or stdin, decodes through `Breadtif(&b, CRGB24)`, displays through libdraw unless suppressed, and can write Plan 9 raw-image output.

Flags mirror the other image tools: compressed output, uncompressed `-9`, grayscale, true-color, RGBV, and error-diffusion control. Output conversion either keeps decoded `CY`/`CRGB24` when true-color output is selected or remaps with `torgbv`.

Memory cleanup frees converted images only when distinct from decoded images, then frees decoded channels and the array.
