# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_internal.h

## Scope And Purpose

`zstd_internal.h` is the shared internal contract for Zstd compression, decompression, and dictionary-building code. It defines constants, error-return macros, entropy defaults, sequence storage structures, block metadata, hot copy helpers, and internal declarations that must stay consistent across modules.

Complete file read: 447 lines.

## Main Components

- Dependency setup enables static-linking-only APIs for Zstd, FSE, HUF, and xxhash internals.
- Error helpers `RETURN_ERROR_IF`, `RETURN_ERROR`, and `FORWARD_IF_ERROR` return encoded Zstd errors and add debug logging when enabled.
- Shared constants define frame/block header sizes, repcode counts, minimum match length, literal/match/offset symbol limits, FSE log limits, and default normalized distributions.
- `ZSTD_copy8`, `ZSTD_copy16`, `COPY8`, `COPY16`, and `ZSTD_wildcopy` provide optimized copy primitives that may intentionally over-read/write within documented overlength bounds.
- `ZSTD_limitCopy` copies up to destination capacity.
- `seqDef`, `seqStore_t`, and `ZSTD_sequenceLength` define the internal sequence stream emitted by match finders.
- `ZSTD_getSequenceLength` expands long literal or match lengths tracked out of band.
- `ZSTD_frameSizeInfo` and `blockProperties_t` describe compressed/decompressed frame and block metadata.
- Internal declarations expose sequence-store access, sequence-code conversion, custom memory allocation, repcode invalidation, compressed-block size parsing, and sequence-header decoding.
- `ZSTD_highbit32` provides compiler-specific or fallback high-bit calculation used throughout compression cost and offset coding.

## Integration Points

This header is included by the Zstd compression and decompression implementation files. Its constants and table definitions must match the bitstream format and the decoder's expectations.

## Notes

- `ZSTD_wildcopy` is performance-critical and deliberately permits bounded overrun behavior; callers must provide adequate buffer slack.
- The default normalized tables and symbol bit tables are format-sensitive.
- The error macros depend on encoded `ERROR(...)` values from `error_private.h`.
