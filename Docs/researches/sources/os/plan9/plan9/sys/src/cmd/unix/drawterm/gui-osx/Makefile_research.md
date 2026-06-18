# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/Makefile

Read fully: 19 lines, 220 bytes. SHA-256 prefix: `c1568f24931ca68a`.

This makefile builds the OS X GUI backend archive `libgui.a` for drawterm.

It includes `../Make.config`, compiles `alloc`, `cload`, `draw`, `load`, and `screen` objects, archives them, and runs `ranlib`.

Integration: invoked by the top-level drawterm makefile through `gui-$(GUI)/libgui.a`.

Risk notes: only the small wrapper files listed in this group were in scope; `load.c` and `screen.c` are referenced but not part of this batch.
