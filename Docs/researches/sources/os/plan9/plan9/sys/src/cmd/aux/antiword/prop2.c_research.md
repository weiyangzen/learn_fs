# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop2.c

## Summary
`prop2.c` parses property information for WinWord 1 and WinWord 2 files. It handles document properties, sections, header/footer offset tables, paragraph/table row properties, character/font runs, and picture references.

## Main Responsibilities
- Defines `iGet2InfoLength()` to advance through WinWord 1/2 sprm/property streams.
- Reads document properties including header/footer specification, default tab width, and DTTM dates.
- Parses section PLCs, section property pages, and header/footer character-position tables.
- Detects table cells/end-of-row markers and extracts column widths/border flags.
- Parses paragraph properties for alignment, numbering, tab changes, indents, and spacing.
- Reads paragraph and character BTE pages, extending page lists from header counters when needed.
- Applies WinWord 1 and WinWord 2 character property formats to font records.
- Extracts picture offsets from character property data and adds them to the picture list.

## Key Dependencies
Uses direct file reads, stylesheet/font defaults, row/style/font/picture list builders, character-position mapping helpers, and `antiword.h` Word constants.

## Filesystem Relevance
Reads structured Word file pages from offsets. It is format parsing, not filesystem implementation.

## Notes
The parser includes defensive length checks around malformed table definitions and property runs.
