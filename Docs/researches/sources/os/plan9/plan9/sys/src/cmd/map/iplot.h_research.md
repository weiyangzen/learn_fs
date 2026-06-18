# File Research: sources/os/plan9/plan9/sys/src/cmd/map/iplot.h

Read fully: 51 lines, 1398 bytes. SHA-256 prefix: `727f7ccda4947686`.

This header provides plot-style drawing macros that emit textual plotting commands via `print()`. It is an alternative to `plot.h`.

Macros include `openpl`, `closepl`, `erase`, `point`, `range`, `text`, `vec`, `move`, `pen`, color constants, `colorcode`, and `colorx`. Text is quoted only when it starts with a space.

Integration: map/plot code can include this header to target a command-stream plotting backend.

Risk notes: all drawing APIs are macros with direct `print()` side effects. Arguments may be evaluated in macro contexts.
