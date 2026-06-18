# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_vms.c

Purpose: Provides VAX/VMS-specific Ghostscript platform support: process exit conventions, time conversion, printer/file handling, wildcard enumeration via RMS, and VMS path-combining semantics.

Key interfaces: `gp_do_exit`, `gp_get_realtime`, `gp_cache_insert`, `gp_cache_query`, `gp_getenv_display`, `gp_open_printer`, `gp_open_scratch_file`, `gp_fopen`, file enumeration functions, `gp_file_name_root`, separator/current/parent helpers, and `gp_file_name_combine`.

Control flow: VMS exit maps Ghostscript success/failure to VMS status constants. Time is computed by subtracting a VMS binary time for 1-Jan-1980 from current VMS system time. Wildcard enumeration rewrites `?` to `%`, removes backslash quoting, appends `.*` for bare `*`, then drives `LIB$FIND_FILE`. Path combining handles device/logical roots, bracketed directories, `]`, `.`, and `-` parent-like syntax before delegating difficult reduction to `gp_file_name_combine_generic`.

Dependencies: Uses VMS descriptors and system services (`SYS$BINTIM`, `SYS$GETTIM`, `LIB$SUBX`, `LIB$EDIV`, `LIB$FIND_FILE`), Ghostscript memory descriptors, and VMS-specific `fopen` record attributes.

Risks and notes: Persistent cache functions are stubs. Scratch-file creation uses `mktemp`. Some VMS path logic is highly specialized and includes comments about Ghostscript-specific extended syntax, so changes need cross-platform path regression coverage.
