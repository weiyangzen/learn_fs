# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/sectlist.c

Linked-list storage for Word section metadata.

Key routines:
- `vDestroySectionInfoList()` frees stored section records.
- `vAdd2SectionInfoList()` appends a section record and its character position.
- `vGetDefaultSection()` initializes default section state with `bNewPage = TRUE`.
- `pGetSectionInfo()` finds section metadata for a character position, falling back to the previous section.
- `tGetNumberOfSections()` and `ucGetSepHdrFtrSpecification()` expose section counts/header-footer flags.

Important behavior:
- If no section records exist, the first lookup creates a default section at character position zero.
- `pGetSectionInfo()` accepts either exact `ulCharPos` or `ulCharPos + 1`, matching Word boundary behavior.

Dependencies:
- `section_block_type`, allocation helpers, parser-generated section lists.

Research relevance:
- Supplies rendering code with page/section transition and header/footer behavior.
