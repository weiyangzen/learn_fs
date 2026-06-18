# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_macio.c

Read status: complete.

Purpose: Classic Mac OS / Carbon file, stdio, resource, path, and font-enumeration support for Ghostscript.

Major areas:
- HFS path conversion between `FSSpec` and colon-separated Mac paths.
- Mac-specific environment behavior for `GS_LIB`.
- Redirection of Ghostscript stdin/stdout/stderr streams through the DLL callback.
- Printer/scratch/file handling.
- Mac resource fork reads.
- Mac path-combine helper semantics.
- Native font enumeration through Font Manager and FOND resources.

Main logic:
- `convertSpecToPath` walks parent directories with `PBGetCatInfoSync` and builds a colon-separated HFS path.
- `convertPathToSpec` creates an `FSSpec` from a path string.
- `getenv("GS_LIB")` builds an Application Support based Ghostscript library/font path.
- `gs_iodev_macstdio` is a pseudo IODevice that patches `%stdin`, `%stdout`, and `%stderr` open routines.
- `mac_stdin_read_process`, `mac_stdout_write_process`, and `mac_stderr_write_process` route data through `pgsdll_callback`.
- `gp_open_printer` uses a scratch file for default output or opens a named file.
- `gp_open_scratch_file` creates a temporary name, resolves the Mac temporary folder when no volume separator is present, and opens it.
- `gp_read_macresource` opens a file resource fork, loads a resource by type/id, returns its size, and optionally copies its bytes into the caller buffer.
- File enumeration is effectively unsupported: it stores the pattern and then returns no entries.
- Mac path helpers use `:` as separator, `::` for parent, and treat empty path items as meaningful.
- Font enumeration uses `FMCreateFontIterator`, `FMGetNextFont`, Font Manager metadata, and FOND resource parsing to return PostScript-ish names and paths, including `%macresource%...#sfnt+id` or `%macresource%...#POST`.

Filesystem/storage relevance:
- This is the main Mac filesystem abstraction for Ghostscript in this group.
- It covers HFS path syntax, temporary files, resource forks, and native font file/resource discovery.

Notable behavior and risks:
- Uses many fixed 256-byte buffers.
- File enumeration is declared unsupported and always ends immediately.
- `getenv("GS_LIB")` allocates a returned string and does not provide ownership clarity.
- FOND parsing directly interprets resource bytes by offset because the Carbon API deprecated the struct view.
