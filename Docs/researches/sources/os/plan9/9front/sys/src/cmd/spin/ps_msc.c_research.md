# File Research: sources/os/plan9/9front/sys/src/cmd/spin/ps_msc.c

## Purpose

`ps_msc.c` generates a PostScript message sequence chart (MSC) from a Spin simulation or trail run. It supports Spin's `-M` style output path by recording per-depth labels, process columns, rendezvous arrows, and process lifelines, then writing a multipage `.ps` file.

## PostScript Template and Layout

`PsPre[]` contains the PostScript prolog: document comments, ISO font encoding, color adjustment, and a `DrawText` procedure. Layout constants define page width/height, margins, process-column spacing, vertical step spacing, and process-header height. `MH` can be scaled when the number of processes exceeds the page width.

Global arrays store chart state:

- `I`: initial process labels;
- `D` and `R`: mappings between real trail depth and local rendered depth;
- `M`: x/process-column location for each local depth;
- `T`: matching local depth for arrows;
- `L`: text labels at local depths;
- `ProcLine`: which process lifelines have already been drawn on the current page.

`TotSteps` defaults to about forty pages of vertical steps but is recalculated from a trail file when `s_trail` is active.

## Output Lifecycle

`putprelude()` opens `<model>.ps`, emits the PostScript header/prolog, sizes internal arrays, optionally counts trail lines to determine `TotSteps`, and starts the first page. `putpostlude()` flushes remaining pages, writes the trailer and final page count, closes the file, reports the output filename to stderr, and exits.

`startpage()` increments page count, writes the page header and legend, emits initial process boxes, sets a clipping region, translates to chart coordinates, clears `ProcLine`, and applies scaling if needed. `putlegend()` prints the Spin version, model filename, MSC label, and page number.

## Drawing Primitives

`psline()` emits colored lines with coordinate conversion from chart coordinates to PostScript coordinates. `colbox()` fills a rectangular box. `putgrid()` draws blue lifelines for process columns as needed. `stepnumber()` draws a gray horizontal guide line and the original trail depth number.

`spitbox()` draws a colored event box and centered label. Colors are inferred from label content: `~B`, `~G`, and `~R` prefixes force blue/green/red; labels containing `!` are white, labels containing `?` are cyan, and other labels are yellow. At depth zero it also records process labels in `I`.

## Pagination and Event Recording

`putbox()` records the current event's process column and tracks maximum x. `pstext()` stores text either as an initial process label at depth zero or as a normal event label at the current logical depth, updating `D`, `R`, and `L`.

`putarrow()` records a message/rendezvous match between two real depths by translating them through `D`. `putpages()` performs final rendering: it scales wide charts, redraws initial process boxes, paginates by vertical position, draws cross-page arrows using positive/negative `T` entries, prints event boxes, frees label strings, and emits final `showpage`.

`dotag()` is the integration point used when Spin emits tagged simulation output. In two-column MSC mode (`columns == 2`) it routes labels to `pstext()` using either trail process number `pno` or current run-list PID. Otherwise it prints textual tags with indentation.

## Notable Risks and Behaviors

- `putpostlude()` exits the process after writing the PostScript file.
- The renderer uses fixed-size assumptions such as `ProcLine` allocated for 1024 bytes but cleared for 256 chars per page.
- Labels are inserted into PostScript strings without visible escaping in this file, so unusual label text could affect generated PostScript syntax.
- `putpages()` frees label strings after rendering; labels should not be reused afterward.
