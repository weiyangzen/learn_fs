# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/Makefile

Win32 GUI backend archive build recipe.

Key responsibilities:
- Includes `../Make.config`.
- Builds `libgui.a` from `alloc`, `cload`, `draw`, `load`, and `screen` objects.
- Archives with `$(AR)` and indexes with `$(RANLIB)`.

Role in this group:
- Selects the Win32-specific wrappers and `screen.c` implementation used by drawterm’s portable build.

Notable risks:
- The object list excludes `wstrtoutf.$O` even though `screen.c` uses `wstrutflen()`/`wstrtoutf()`, so this function must be supplied elsewhere or the makefile can produce an unresolved symbol depending on the full build.
