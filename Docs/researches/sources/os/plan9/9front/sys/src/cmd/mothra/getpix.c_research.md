# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/getpix.c

Loads, decodes, optionally resizes, caches, and frees images for Mothra rich text.

Key behavior:
- Keeps per-page `Pix` cache entries keyed by image URL string plus requested width/height.
- Resolves image URLs relative to the page URL, fetches them, detects type, pipes through format decoders (`gif`, `jpg`, `png`, `bmp`, `ico`), and optionally through `resize`.
- Reads decoded images with `readimage()` and stores them on the matching `Rtext`.
- `getpix()` forks worker processes with shared memory to fetch/decode multiple images concurrently, limited by `NXPROC`.
- Provides byte-size counting and cache cleanup.

Important dependencies: Mothra URL/pipeline helpers, Plan 9 image decoders, `draw`, `RFMEM` shared-memory rfork.

Notable risks:
- Parallel workers mutate shared `Www`/`Rtext` state under `RFMEM` without explicit locks.
- Unknown image types become textual `[img: ...]` errors.
