# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/g3p9bit/g3p9bit.c

`g3p9bit.c` decodes Group 3 fax data into Plan 9 bitmap output. It supports raw fax-like streams plus a couple of PC/digifax header formats, builds white/black Huffman decode tables from included `wtab`/`btab` data, synchronizes on EOL codes, and reconstructs black pixel runs into a fixed-width bitmap.

Options simulate 2-bit gray horizontal compression and duplicate scanlines vertically. Output begins with a Plan 9 bitmap header followed by row data written in manageable chunks.
