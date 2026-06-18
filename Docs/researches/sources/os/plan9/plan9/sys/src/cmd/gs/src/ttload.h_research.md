# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttload.h

## Role

`ttload.h` declares TrueType table loader functions and defines stream/reader convenience macros for table parsing.

## Main Responsibilities

- Declares loader functions for many TrueType tables:
  - directory, maxp, gasp, header, hhea, loca, names, CVT, cmap, hmtx, programs, OS/2, post, hdmx, and arbitrary table data.
- Declares cleanup helpers for names and hdmx tables.
- Defines byte-order reader macros:
  - `GET_Byte`, `GET_UShort`, `GET_Short`, `GET_Long`, `GET_ULong`.
- Contains legacy FreeType stream/frame macros split by `TT_CONFIG_REENTRANT`.

## Important Implementation Details

- In this Plan 9/Ghostscript port, the active reader macros call `ttfReader__*` helpers on a local `r`.
- Reentrant and thread-safe macro sections preserve older FreeType loader conventions, though this group’s active implementation in `ttload.c` mostly uses the direct `ttfReader` path.
- The header exposes a broader loader API than the small subset implemented in this grouped `ttload.c`.

## Cross-File Relationships

- Included by `ttload.c` for parsing macros and prototypes.
- Included by `ttobjs.c`, where `Face_Create` uses `Load_TrueType_MaxProfile`, `Load_TrueType_CVT`, and `Load_TrueType_Programs`.
- Depends on `ttcommon.h` and forward-declared face types.

## Notable Risks / Review Notes

- The prototype surface is wider than the implementations present in this group, so some functions are expected to be in other files or omitted by this port.
- Macro-based parsing relies on a correctly named local reader variable `r`, which is fragile but consistent with the local code.
