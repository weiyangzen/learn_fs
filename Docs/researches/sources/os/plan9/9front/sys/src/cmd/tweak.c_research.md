# File Research: sources/os/plan9/9front/sys/src/cmd/tweak.c

`tweak` is an interactive graphical editor for Plan 9 images, face files, cursor files, and subfonts. It uses libdraw/event/plumb, maintains a linked list of open `Thing` objects, and supports magnified pixel editing plus parent/child edit views.

It can open regular images, legacy hex face files, cursor files, and subfont-bearing image files. `drawthing()` lays out each object, renders magnified pixels, shows metadata, and keeps child edit panes synchronized. Text metadata fields are clickable and editable for file name, depth, rectangle, subfont metrics, offsets, character widths, and magnification.

Mouse interactions support opening subregions or glyphs, twiddling pixels with configurable button values, sweeping/copying pixel regions, inspecting pixel values, writing files back in the original-ish format, re-reading, closing, and opening glyph ranges. It also handles plumber `imageedit` messages and temporary files for `showdata`.
