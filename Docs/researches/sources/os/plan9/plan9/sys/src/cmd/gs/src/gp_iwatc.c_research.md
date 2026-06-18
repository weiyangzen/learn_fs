# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_iwatc.c

Read status: complete.

Purpose: Intel/Watcom C-specific platform routines for Ghostscript on DOS-like systems.

Main logic:
- `gp_init` initializes a private `gs_stdprn` pointer and installs a `SIGFPE` handler.
- Floating-point exceptions print “Numeric exception” and exit.
- Persistent cache functions are stubs.
- `gp_open_printer` handles `PRN`/empty printer output, including special binary handling for Watcom `stdprn`; otherwise opens a named file.
- `gp_close_printer` closes non-`stdprn` streams and resets `gs_stdprn`.
- `gp_open_scratch_file` builds a temporary filename from a prefix and temp directory, lowercases the temp path to protect `X` placeholders, appends `XXXXXX`, calls `mktemp`, and opens with `gp_fopentemp`.
- `gp_fopen` delegates to `fopen`.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Implements scratch file creation and printer file access for Watcom/DOS builds.

Notable behavior:
- Uses `mktemp`, which is inherently race-prone on modern systems.
- Uses fixed `gp_file_name_sizeof` limits and DOS path assumptions.
