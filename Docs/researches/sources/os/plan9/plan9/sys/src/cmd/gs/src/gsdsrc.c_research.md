# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdsrc.c

## Role

`gsdsrc.c` implements Ghostscript data-source GC support and accessors for string/byte/float/stream-backed data sources.

## Main Behavior

Defines `st_data_source` GC descriptor. Enumeration/relocation treats data differently by type:

- string: const string pointer
- stream: stream pointer
- bytes/floats: raw byte data pointer

Accessors:

- `data_source_access_string`
- `data_source_access_bytes`
- `data_source_access_stream`

String and byte access are identical except for GC handling and do not bounds-check. They either return a direct pointer or copy into caller buffer.

Stream access first tries to satisfy the request from the current stream buffer if the requested range is already buffered. Otherwise it seeks and reads exactly the requested length, returning `rangecheck` on seek/read failure or short read.

## Dependencies

Uses `gsdsrc.h`, stream APIs, memory helpers, and Ghostscript errors.

## Risks

String/byte accessors explicitly do not bounds-check; callers must validate ranges. Stream access may change stream position via `sseek`/`sgets`, so callers sharing streams must account for side effects.
