# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/mmc.c

This file implements the MMC/SCSI CD/DVD/BD drive backend for `cdfs`.

Key behavior:
- Probes MMC devices, reads capabilities, optional write parameter page, speed info, and installs `mmcdev` methods.
- Implements mode sense/select helpers for 6-byte and 10-byte MMC mode pages.
- Reads mechanism status, starts/stops/ejects/ingests media, and adjusts drive caching.
- Disc discovery:
  - reads track info, disc info, TOC, DVD/BD disc structures, and MMC configuration features;
  - infers CD tracks for non-writers;
  - detects CD, DVD minus/plus, BD, layer suffixes, recordable/erasable state, write availability, and next writable address.
- Track I/O:
  - opens read tracks with buffered `READ CD` or `READ(12)`;
  - creates writable tracks with proper block size/write-parameter setup;
  - writes with `WRITE(10)` or write-and-verify where appropriate;
  - closes/syncs tracks and handles final lead-out.
- Media management:
  - formats BD/DVD rewriteable media as needed;
  - reserves DVD-R tracks;
  - closes sessions/finalizes discs;
  - blanks or quick-blanks rewriteable media;
  - handles `format`, `blank`, `quickblank`, `eject`, `ingest`, and speed controls.

Important details:
- BD-R may be formatted on first configuration read to allocate spares before writing.
- Write-once media writes are deliberately not retried by the write path to avoid invalid duplicate writes.
- `Readblock` and read CDB sizing are chosen to avoid remote 9P transfer failures.
- The code reconciles drive-reported and computed next writable addresses conservatively and logs disagreements.
- BD capacity is used to infer single/dual/triple/quad layer suffixes.

Filesystem relevance:
- Direct. This is the device implementation that makes `cdfs` track files readable and writable over 9P.
