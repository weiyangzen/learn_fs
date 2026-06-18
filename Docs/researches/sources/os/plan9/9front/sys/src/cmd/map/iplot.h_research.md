# File Research: sources/os/plan9/9front/sys/src/cmd/map/iplot.h

`iplot.h` is an alternate plotting macro header for V8/V9-style systems. It maps plot operations to textual commands printed with `print()`: open/close, erase, point, range, text, vector, move, pen style, and color.

It also defines color abbreviations and a `colorcode()` helper. There is no state or function implementation beyond macros.
