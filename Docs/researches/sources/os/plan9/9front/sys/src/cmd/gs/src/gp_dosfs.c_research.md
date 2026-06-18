# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dosfs.c

Common MS-DOS and DesqView/X filesystem helper routines.

Key behavior:
- Uses DOS ioctl interrupt calls to set device file handles into binary or text mode.
- Provides `gp_setmode_binary`.
- Defines DOS-style file-list separator `;`, binary suffix `b`, and binary modes `rb`/`wb`.
- Implements Windows/DOS path root detection including drive letters, root slashes, and UNC paths.
- Provides path separator, parent/current directory, and path-combination helper functions that delegate to `gp_file_name_combine_generic`.

Notable dependencies:
- DOS register APIs from `dos_.h`.
- Generic path-combination helper from `gpmisc.h`.

Research notes:
- This is path and file-mode glue, not file enumeration; DOS enumeration is in `gp_dosfe.c`.
