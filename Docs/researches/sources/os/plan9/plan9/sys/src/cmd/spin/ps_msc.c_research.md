# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/ps_msc.c

This file generates PostScript message sequence chart output for Spin simulation runs, supporting Spin’s `-M` style MSC output.

Main state:
- `PsPre[]` is a PostScript prolog defining text rendering, ISO encoding, and color adjustment.
- Page geometry constants define page width/height, margins, process-line spacing, step spacing, and process tag height.
- Arrays `I`, `D`, `R`, `M`, `T`, and `L` map simulation depth to rendered rows, labels, process columns, and message arrows.
- `ProcLine` tracks which process lifelines have already been drawn on a page.
- `pspno`, `ldepth`, `maxx`, `TotSteps`, and `Scaler` track pagination, scaling, and chart extent.

Major functions:
- `putprelude()` creates `<model>.ps`, writes headers/prolog, optionally counts trail length, allocates chart arrays, and starts the first page.
- `startpage()` writes page headers, legend, process headers, clipping region, and coordinate transform.
- `putlegend()` prints Spin version, model file name, MSC label, and page number.
- `spitbox()` draws colored event boxes, with color selected by message marker or by send/receive symbols.
- `putarrow()` records matching send/receive relationships by depth index.
- `putpages()` performs final pagination, draws step numbers, boxes, lifelines, and red arrows, handling arrows crossing page boundaries.
- `pstext()` records process labels/events during simulation.
- `dotag()` either routes MSC-tagged text into PostScript mode or prints normal simulation text.

Integration:
- `sched.c` uses `pstext()` when `columns == 2`.
- `run.c` printing functions eventually call `dotag()`.
- Trail replay affects `TotSteps` by counting lines from the trail file.

Risk notes:
- Fixed-size strings and manual `sprintf` are used for output names and labels.
- Long labels can affect box width but there is no deep escaping for arbitrary PostScript-special characters beyond normal formatted insertion.
- The module exits the process in `putpostlude()` after finalizing the PostScript file.
