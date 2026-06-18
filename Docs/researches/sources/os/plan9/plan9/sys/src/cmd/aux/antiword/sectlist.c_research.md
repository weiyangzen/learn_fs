# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/sectlist.c

This file stores Word section information in a linked list.

Key behavior:
- Adds section records keyed by character position.
- Provides default section initialization with `bNewPage = TRUE`.
- `pGetSectionInfo()` returns the first section, a section matching a character position, or the previous section if no match is found.
- `tGetNumberOfSections()` counts records.
- `ucGetSepHdrFtrSpecification()` retrieves header/footer flags by section number.

Important details:
- If no section records exist, the getter creates a default section at character position zero.
- It treats `ulCharPos` and `ulCharPos + 1` as equivalent for lookup.

Filesystem relevance:
- Indirect: maps parsed file character positions to section rendering state.
