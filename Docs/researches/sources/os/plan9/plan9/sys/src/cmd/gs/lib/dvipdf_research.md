# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/dvipdf

Shell wrapper converting DVI to PDF through `dvips` and Ghostscript.

Behavior:

- Collects leading options for Ghostscript.
- Accepts `input.dvi` and optional `output.pdf`; otherwise derives the output name from the input basename.
- Pipes `dvips -q -f "$infile"` into `gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="$outfile" ... -c .setpdfwrite -`.
- Passes options twice because `-I` only takes effect before other options.

This script is a document-conversion wrapper only.
