# File Research: sources/local-fs/xfsdump/restore/namreg.c

## Summary
Implements the restore name registry. It stores directory-entry names in a persistent housekeeping file and returns compact offset handles used by tree nodes.

## Main Responsibilities
- Create or reopen the `namreg` housekeeping file.
- Store persistent append offset in the first page.
- Append names as one-byte length plus raw name bytes.
- Buffer append writes for performance.
- Resolve a name handle back to a NUL-terminated name.
- Optionally mmap the name payload area for faster lookups after all names have been added.

## Important Behavior
`namreg_init()` creates a prefilled file sized from `inocnt * NAMREG_AVGLEN` for new restores, or reopens an existing file for resume. It mmaps the first page as `namreg_pers_t`.

`namreg_add()` flushes/seeks to append position when needed, buffers one length byte plus the name, advances `np_appendoff`, and returns the previous file offset as the handle.

`namreg_flush()` writes the buffered name data to disk and resets the in-memory buffer offset.

`namreg_get()` converts the handle to a file offset, then either indexes the mmapped name area or seeks and reads up to 256 bytes into a static buffer. It copies the name into the caller buffer and NUL-terminates it.

`namreg_map()` flushes pending names and mmaps the payload region after the persistent page; if mapping fails, it falls back to seek/read lookup.

`namreg_del()` is intentionally unimplemented; the registry grows for the life of the restore state.

## Dependencies
Depends on `open_pathalloc()`, `create_filled_file()`, `mmap_autogrow()`, xfsdump locking, logging, page-size globals, and optional `NAMREGCHK` handle check bits.

## Risks
Names are limited to 255 bytes by assertion. A release build with assertions disabled would still store the length in one byte and truncate modulo 256.

`namreg_get()` reads the stored length through `char`; on platforms where `char` is signed, lengths above 127 can become negative before conversion to `size_t`.

The static read buffer is protected by the global `lock()`, but the mmap lookup path still shares global registry state and is not independently reentrant.

Deletion is a no-op, so long or repeated restores accumulate dead name records in the housekeeping file.

Short reads in `namreg_get()` are accepted as long as `read()` returns positive; the code does not verify that the full length byte plus name was read before copying.
