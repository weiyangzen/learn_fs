# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/totif.c

Command-line TIFF converter. It reads a Plan 9 image, optionally converts its channel descriptor, and writes TIFF via `memwritetif`.

Options select output channel (`GREY1`, `GREY4`, `GREY8`, `CMAP8`, `BGR24`) and compression (`none`, Huffman, T4, T4 2D, T6, LZW, LZW predictor, PackBits). Fax compression forces bilevel output.

`memtochan` performs channel conversion with `memimagedraw`; unsupported or unsuitable input channels are converted before writing.
