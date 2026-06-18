# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_ntfs.c

Windows NT/Win32 filesystem support, adapted from DOS filesystem support.

Key behavior:
- Sets binary/text file mode through `_setmode` or `setmode`.
- Defines Windows-style file-list separator, binary suffix, and binary modes.
- Implements file enumeration with `FindFirstFile` and `FindNextFile`.
- Removes Ghostscript escape backslashes before passing patterns to the OS.
- Skips `.` and `..` and directory entries during enumeration.
- Reattaches the directory prefix to returned file names.
- Provides Windows/DOS path root and separator helpers and delegates path combination to `gp_file_name_combine_generic`.

Notable dependencies:
- Windows file APIs and Ghostscript GC descriptors.

Research notes:
- Directory wildcard limitations are documented in comments.
- The enumeration truncation behavior returns `maxlen` or `0` depending on whether any prefix can fit.
