# File Research: sources/os/bsd/netbsd-src/lib/libpanel/panel.h

Read completely: 61 lines.

This public header declares opaque `PANEL` and the libpanel API: create/delete, replace/window access, user pointer set/get, hide/show/hidden, top/bottom, above/below, move, and `update_panels`.

It includes `<curses.h>` and wraps declarations in C linkage macros.

Security/reliability notes: public ABI exposes user pointer as `char *`, though callers may use it as arbitrary data by convention.
