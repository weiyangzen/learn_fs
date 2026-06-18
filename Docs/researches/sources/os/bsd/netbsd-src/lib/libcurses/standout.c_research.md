# File Research: sources/os/bsd/netbsd-src/lib/libcurses/standout.c

Implements standout-mode convenience APIs: `standout`, `standend`, `wstandout`, and `wstandend`.

`wstandout` sets `__STANDOUT` in `win->wattr` only if the terminal can enter/exit standout mode or underline characters. `wstandend` resets the window attribute set to `__NORMAL`.
