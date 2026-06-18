# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writeppm.c

Netpbm writer for Plan 9 `Image`/`Memimage`. It supports PBM, PGM, and PPM output in raw or text mode through `writeppm` and `memwriteppm`.

Channel support includes `GREY1`, `GREY2`, `GREY4`, `GREY8`, and `RGB24`. It emits the correct magic (`P1`-`P6`), optional comment, dimensions, max sample where required, and scaled or raw pixel data.

Packed gray pixels are extracted with bit masks; RGB24 output swaps Plan 9 byte order into PPM RGB order.
