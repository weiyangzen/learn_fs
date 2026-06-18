# File Research: sources/os/bsd/netbsd-src/lib/libcurses/insch.c

Implements narrow character insertion: `insch`, `mvinsch`, `mvwinsch`, and `winsch`.

`winsch` shifts the current line one cell right from the cursor, writes the incoming `chtype` with window background/color merging, copies background non-spacing characters under wide builds, marks the line dirty, and handles the bottom-right scroll case when `__SCROLLOK` is enabled.
