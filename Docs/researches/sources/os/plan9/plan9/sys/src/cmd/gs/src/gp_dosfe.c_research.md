# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dosfe.c

Read status: complete.

Purpose: MS-DOS file enumeration implementation for Ghostscript.

Main logic:
- Defines `file_enum_s` containing DOS find state, original and translated patterns, header length, first-time flag, and Ghostscript memory pointer.
- `gp_enumerate_files_init` copies the original pattern and builds a DOS-compatible pattern after it in the same allocation.
- Translates `*` to DOS-friendly matching and adds `*.*` when needed because DOS does not treat bare `*` as all files.
- Tracks the directory/header portion through the last `:`, `/`, or `\`.
- `gp_enumerate_files_next` calls `dos_findfirst`/`dos_findnext`, reconstructs the full returned name, removes DOS space padding, and filters with Ghostscript `string_match`.
- `gp_enumerate_files_close` frees pattern and enumerator through Ghostscript memory.

Filesystem/storage relevance:
- Implements wildcard file enumeration over DOS filesystems for the `%os%` file device layer.

Notable behavior:
- Comments note DOS wildcard limitations in directory components and backslash handling.
- Returns `~(uint)0` when enumeration is complete.
