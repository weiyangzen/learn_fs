# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdsrc.h

## Role

`gsdsrc.h` defines `gs_data_source_t`, a uniform embedded source descriptor for data used by color maps, images, and similar constructs.

## Data Sources

Supported source types:

- string
- bytes
- floats
- stream

The structure stores an access procedure, source type, and either a `gs_const_string` or `stream *`.

## API

Defines access-procedure signature and helper macros:

- `data_source_access_only`
- `data_source_access`
- `data_source_copy_only`
- `data_source_copy`

Defines initialization macros for string, byte, float, and stream sources. Float arrays are represented as byte spans with `sizeof(float)` scaling.

Also declares `st_data_source` for GC tracing.

## Dependencies

Includes `gsstruct.h`, forward-declares `stream`, and expects Ghostscript string/byte/ulong types.

## Risks

The header states access procedures may or may not bounds-check. The `data_source_access` macro returns from the enclosing function on error, so it must only be used in functions returning Ghostscript integer status codes.
