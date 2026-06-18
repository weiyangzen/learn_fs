# sources/user-network-fs/samba/source3/printing/nt_printing_os2.c

Purpose: maps Windows printer driver names to OS/2 driver names using the configured `os2 driver map` file, with a single-entry process-local cache for the last successful mapping.

Important APIs and functions: `spoolss_map_to_os2_driver()` validates the input driver pointer, checks whether a map file is configured, returns the cached mapping when possible, loads the map file with `file_lines_load()`, parses `windows=OS/2` lines, trims whitespace, skips comments, and replaces `*pdrivername` with a talloc-owned OS/2 name on match. `set_driver_mapping()`, `get_win_driver()`, and `get_os2_driver()` maintain the static cache.

Control flow: if no map file is configured, the function returns `WERR_FILE_NOT_FOUND`. Empty or unreadable maps return `WERR_EMPTY`. A non-matching map is not an error; it leaves the original driver name in place and returns `WERR_OK`.

State and persistence: map data is read from a configured file. The only in-process state is `win_driver` and `os2_driver`, both replaced with heap-allocated copies after a successful match.

Dependencies and integration: integrates with spoolss code that needs OS/2-compatible driver names. It depends on loadparm substitution, Samba file-line utilities, string helpers, and WERROR conventions.

Risks: the static cache is global and not keyed by mapfile path, so a configuration reload changing the map file could keep serving one stale mapping until another mapping is found. `set_driver_mapping()` failure is ignored before duplicating `os2_name`, losing cache but not the returned mapping. Tests should cover whitespace, comments, missing `=`, repeated lookups, no configured map, empty map, non-match success, and allocation failures.
