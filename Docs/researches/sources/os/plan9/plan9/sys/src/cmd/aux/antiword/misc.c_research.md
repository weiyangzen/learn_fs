# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/misc.c

## Summary
`misc.c` provides shared utility code for Antiword’s Plan 9 tree copy: platform directory lookup, regular-file sizing, compound-document block reads, output-list splitting, number formatting, Unicode/string helpers, locale-to-mapping selection, and Word timestamp conversion.

## Main Responsibilities
- Resolves user/global Antiword configuration directories, with Plan 9 using the `home` environment variable and header-defined Antiword paths.
- Validates regular files and obtains sizes via `stat` outside RISC OS.
- Implements `bReadBytes()` and `bReadBuffer()` for reading OLE-style chained big/small block streams.
- Converts Word color IDs, Roman/alpha list numbers, UCS characters to UTF-8, and Word DTTM timestamps.
- Splits `output_type` linked lists at whitespace or hyphen boundaries for wrapping.
- Selects default character mapping files from locale codesets.

## Key Dependencies
Uses `antiword.h`, low-level Word helpers such as `ulDepotOffset()`, `usGetWord()`, `ulTranslateCharacters()`, allocation wrappers, debug/fail macros, and output-width helpers.

## Filesystem Relevance
This file is the closest in this group to direct filesystem behavior: it checks file metadata, seeks/reads document streams, and resolves config/mapping-file locations.

## Notes
`bReadBuffer()` treats damaged block depots as fatal warnings/errors. Locale parsing is environment-driven and predates modern UTF-8-default assumptions.
