# File Research: sources/os/bsd/netbsd-src/lib/libcurses/slk.c

Implements soft label key support.

`slk_init` validates label layout and reserves a bottom ripoff line. Public APIs delegate to screen-safe internals for attributes, colors, hide/restore, label lookup, refresh, touch, narrow label set, and wide label set. `__slk_init` allocates labels and detects terminal-native SLK support; `__slk_ripoffline` binds the ripoff window; `__slk_resize` computes label widths/positions for 3-2-3 or 4-4 layouts; `__slk_set_finalise` trims and justifies printable text by display width; `__slk_draw` writes either terminal labels or the ripoff window, with special handling to avoid scrolling on the final label; `__slk_free` releases windows and label text.
