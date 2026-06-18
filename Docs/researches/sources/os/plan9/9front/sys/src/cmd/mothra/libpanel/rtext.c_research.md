# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/rtext.c

Implements rich-text construction, layout, drawing, scrolling redraws, hit testing, selection, and text snarfing.

Key behavior:
- `pl_rtnew` and wrappers build linked `Rtext` runs containing text, bitmaps, or embedded panels.
- `pl_rtfmt()` formats runs into lines within a galley width, computing rectangles, line links, widths, and total size.
- `pl_rtdraw()` draws visible runs, embedded panels, images, links, selection highlight, and strike-through using an optional backup image.
- `pl_rtredraw()` supports efficient vertical/horizontal scroll redraw by copying existing pixels and drawing exposed regions.
- `pl_rthit()` maps a mouse point to a hot rich-text run.
- Provides selection marking and selected-text extraction.

Important dependencies: libpanel draw/layout primitives, `rtext.h` tab encoding, embedded `Panel` layout.

Notable risks:
- Embedded panels are moved during draw/scroll; their bitmap pointers need correction when a backup bitmap is used.
- Long unbreakable runs are force-fit if line breaking makes no progress.
