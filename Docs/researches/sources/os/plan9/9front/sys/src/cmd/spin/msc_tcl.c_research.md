# File Research: sources/os/plan9/9front/sys/src/cmd/spin/msc_tcl.c

`msc_tcl.c` generates Tcl/Tk message sequence chart output for Spin simulations or trail replays. It records process lanes, step labels, message arrows, and initial process boxes, writes a `.tcl` canvas script, then launches it with `wish`.

`putprelude()` opens `<model>.tcl`, optionally counts trail-file lines to size arrays, and allocates depth-to-chart maps (`D`, `R`), lane positions (`M`), arrow targets (`T`), labels (`L`), and initial process labels (`I`). `pstext()` records either an initial process label at depth zero or a chart event at the current simulation depth.

Rendering is deferred until `putpostlude()`. `putpages()` emits the Tcl window, canvas, scrollbars, grid lines, boxes, labels, and message arrows. `psline()` draws grid or message lines, using distinct colors for rendezvous and asynchronous messages. `spitbox()` chooses box colors from event content and escapes text for Tcl. `putarrow()` connects send/receive depths by mapping simulation depth to chart depth.

`dotag()` is the integration point used by ordinary trace printing: in MSC mode it records chart text by process/lane, otherwise it prints indented trace text. `putpostlude()` writes the final page, closes the Tcl file, prints the random seed, removes `pan.pre`, and executes `wish -f <model>.tcl &`.

Important constraints: process lanes are limited to 256, default max steps starts at `2*4096` but is adjusted from trail length, dimensions are heuristic, strings are only lightly escaped, and the file launch uses `system()`.
