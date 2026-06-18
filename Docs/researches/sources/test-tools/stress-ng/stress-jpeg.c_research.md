# sources/test-tools/stress-ng/stress-jpeg.c

Purpose: implements `jpeg`, a libjpeg compression stressor that generates synthetic RGB images and repeatedly compresses them to memory or `/dev/null`, measuring pixel throughput and compression ratio.

Important APIs/types/functions: image generators include `stress_rgb_plasma()`, `stress_rgb_noise()`, `stress_rgb_brown()`, `stress_rgb_gradient()`, `stress_rgb_xstripes()`, and `stress_rgb_flat()`. `stress_rgb_compress_to_jpeg()` wraps libjpeg setup, scanline submission, optional checksum calculation, and duration measurement. Options control width, height, quality, and image type.

Control flow: `stress_jpeg()` resolves dimensions and quality with maximize/minimize support, mmaps RGB and row-pointer buffers, seeds deterministic random state, generates the selected image once, reports memory usage, sync-starts, and loops compressing the same image. With `--verify`, it performs a second compression and checksum pass each iteration, though the checksums are only computed rather than compared in this file. Metrics are reported after the loop and buffers are unmapped.

State and persistence behavior: all image data and row pointers are anonymous memory. When `open_memstream()` exists, compressed bytes are held in a temporary malloc-backed stream and freed; otherwise output is `/dev/null`.

Dependencies and integration points: compile-gated on libjpeg headers and library. Uses stress-ng mmap, memory naming, metrics, deterministic PRNG, and optional verification flag. Registered as `CLASS_CPU | CLASS_COMPUTE`, verification optional.

Risks: maximum 4096x4096 RGB buffers can consume significant memory per worker. `open_memstream()` availability changes whether compressed size is meaningful. Libjpeg error handling uses the default error manager; fatal libjpeg errors may longjmp/exit depending on library behavior.

Test signals: verify each image type, min/max size and quality, optional verification mode, nonzero megapixels/sec metric, reasonable compression-ratio metric, and clean unmap/free behavior on allocation failure.
