# File Research: sources/local-fs/udftools/mkudffs/mkudffs.h

## Role

Public internal interface for `mkudffs` support functions and media type constants.

## Contents

- Includes `ecma_167.h`, `osta_udf.h`, and `libudffs.h`.
- Defines UDF implementation strings:
  - `UDF_ID_APPLICATION`
  - `UDF_ID_DEVELOPER`
- Defines default media profile indexes used by `defaults.c`.
- Declares `enum media_type` for HD, optical, write-once, rewritable, MO, WORM, and BD-R categories.
- Exports `udf_space_type_str`.
- Declares formatter functions implemented primarily in `mkudffs.c`, plus `calc_space()` which is declared here but not implemented in this file.

## Dependencies

Consumers need the UDF structure definitions from the included UDF headers and `struct udf_disc` from `libudffs.h`.

## Research Notes

This header is the central contract between `mkudffs/options.c`, `mkudffs/main.c`, and the descriptor-building implementation.
