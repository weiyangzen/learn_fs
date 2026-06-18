# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dosfs.c

Read status: complete.

Purpose: common filesystem routines for MS-DOS-like platforms, including DesqView/X.

Main logic:
- `gp_set_file_binary` uses DOS ioctl interrupt `0x44` to set or clear binary mode on device handles.
- `gp_setmode_binary` applies that operation to a `FILE *`.
- Defines DOS filename constants: list separator `;`, binary suffix `b`, modes `rb` and `wb`.
- Implements path-combine helper functions for DOS/Windows-style roots, separators, parent/current directory items, and empty item behavior.
- `gp_file_name_combine` delegates to shared `gp_file_name_combine_generic`.

Filesystem/storage relevance:
- Supplies DOS path syntax and binary/text mode behavior for Ghostscript file handling.

Notable behavior:
- Recognizes UNC-like network paths, absolute slash/backslash paths, and drive-letter roots.
- Treats both `/` and `\` as separators.
