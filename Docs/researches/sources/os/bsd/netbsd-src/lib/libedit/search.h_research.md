# File Research: sources/os/bsd/netbsd-src/lib/libedit/search.h

## Purpose
Private search subsystem state and declarations.

## Main Declarations
- `el_search_t`: pattern buffer/length, last search direction, last character-search direction/target, and `t`-style flag.
- Function declarations for pattern matching, lifecycle, history matching, incremental/vi search, line search, repeat search, and character search.

## Integration
Embedded in `EditLine` and used by `search.c`, command implementations, and history navigation.

## Risks And Notes
Search state persists between commands for repeat-search behavior, so initialization and updates must preserve readline/vi expectations.
