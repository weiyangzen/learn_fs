# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxboth.c

Build-composition source file that includes both stdio-backed and file-descriptor-backed stream implementations.

Key behavior:
- Includes `sfxstdio.c` first, providing normal public `sread_file`, `swrite_file`, `sappend_file`, and `sread_subfile`.
- Defines `KEEP_FILENO_API`, then includes `sfxfd.c`, causing its public entry points to be exposed as `sread_fileno`, `swrite_fileno`, and `sappend_fileno` instead of clashing with stdio names.

Notable dependencies:
- Directly depends on source inclusion rather than separate object linkage.

Research notes:
- This is a legacy compile-time composition technique, not a standalone implementation.
- The resulting build offers both backends in the same executable.
