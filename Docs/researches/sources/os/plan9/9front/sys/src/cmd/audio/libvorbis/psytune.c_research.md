# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psytune.c

Dead/reference utility for running PCM audio through psychoacoustic processing without full encoding.

Important contents:
- File comment explicitly says it is dead code retained for documentation/reference and should not be compiled.
- Defines local psychoacoustic setup structures, partition/coupling tuning, floor setup, mapping info, and codec setup.
- `analysis()` optionally writes vectors to MATLAB-style `.m` files.
- `main()` reads a WAV-like stream from stdin, skips/copies a 44-byte header, processes overlapping stereo frames, runs FFT/MDCT, computes psychoacoustic masks, applies floor/residue/coupling analysis, reconstructs samples, and writes PCM-like output.
- Uses historical helper names such as `_vp_compute_mask`, `_vp_remove_floor`, `_vp_partition_prequant`, and `_vp_couple`.

Integration points:
- Includes many libvorbis internals: `codec_internal.h`, `psy.h`, `mdct.h`, `smallft.h`, `window.h`, `lpc.h`, `lsp.h`, `masking.h`, and `registry.h`.
- Useful as a tuning/reference artifact, not as a live build unit.

Risk and review signals:
- Should not be compiled; it likely does not match current interfaces.
- Uses unchecked I/O, `alloca`-style assumptions through codec helpers, and simplified WAV handling.
- Retained constants may document older tuning intent but should not be treated as authoritative runtime behavior.

Filesystem relevance:
- No filesystem implementation. It performs simple stdin/stdout test I/O for audio tuning.
