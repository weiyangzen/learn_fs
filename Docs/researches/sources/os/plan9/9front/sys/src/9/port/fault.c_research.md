# File Research: sources/os/plan9/9front/sys/src/9/port/fault.c

Portable Plan 9 user fault handling, demand paging, copy-on-write, physical segment mapping, and user address validation.

Key responsibilities:
- Converts trap/fault conditions into notes or process exits through `faultnote()` and `faulterror()`.
- Loads missing text/data/swap pages in `pio()`, including multi-page block reads through device `bread`.
- Resolves segment faults in `fixfault()` for text, data, bss, shared, stack, sticky, fixed, and swapped pages.
- Performs copy-on-write for writable data pages when references or image-cache ownership require private copies.
- Maps `SG_PHYSICAL` segments through `mapphys()` using physical segment attributes.
- Implements the top-level `fault()` loop, including segment lookup, permission checks, low-priority retry, and process-control handling.
- Provides syscall address validation helpers: `okaddr()`, `validaddr()`, `vmemchr()`, `seg()`, and `checkpages()`.

Important behavior:
- Text pages are mapped read-only and cached; writable segments set `PG_MOD|PG_REF`, optionally `PG_PRIV`.
- Stack demand-fill uses byte value `0xfe`; bss/shared use zero-fill.
- On I/O errors while page-in is running, non-interrupt errors become fatal user faults.
- The read/access parameter also drives execute-permission checks for no-exec or non-flushable pages.
- `fixfault()` releases the segment lock before calling `putmmu()`.

Dependencies:
- Depends on `Segment`, `Pte`, `Page`, `Image`, swap helpers, page-cache helpers, `putmmu()`, device read paths, and process note/error machinery.

Notable risks:
- The ternary expression in the permission check is compact and precedence-sensitive.
- `pio()` deliberately unlocks and relocks the segment around I/O, so it must retry because another process or the pager may have raced.
- Physical mappings build a temporary stack `Page` only to satisfy `putmmu()` metadata needs.
