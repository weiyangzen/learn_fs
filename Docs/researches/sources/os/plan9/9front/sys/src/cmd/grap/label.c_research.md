# File Research: sources/os/plan9/9front/sys/src/cmd/grap/label.c

Label generation for graph sides. It tracks point size, text dimensions, label offsets, and optional label width. `label` emits a pic invisible text box positioned relative to the frame side, estimating vertical side label width when needed.

`labelmove`, `labelwid`, and `lab_adjust` accumulate positioning adjustments. `sizeit` wraps strings in troff size escapes, handling absolute and relative size changes with or without a global point size.
