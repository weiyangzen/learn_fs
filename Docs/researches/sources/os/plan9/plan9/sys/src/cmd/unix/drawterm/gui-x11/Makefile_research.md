# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/Makefile

X11 GUI backend archive build recipe.

Key responsibilities:
- Includes `../Make.config`.
- Builds `libgui.a` from `x11.$O` and `keysym2ucs-x11.$O`.
- Archives and indexes the result.

Role in this group:
- Selects the X11 backend plus Unicode keysym conversion table.

Notable risks:
- Build relies on X11 headers/libraries being supplied by the surrounding configuration rather than this makefile.
