# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iccinit0.c

Defines an empty Ghostscript initialization string for non-compiled initialization:
- `gs_init_string[] = { 0 }`
- `gs_init_string_sizeof = 0`

The comment notes `gsmain.c` recognizes an empty init string specially.
