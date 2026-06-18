# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/dvipdf

Shell wrapper converting DVI to PDF by piping `dvips` output into Ghostscript `pdfwrite`.

Behavior:
- Collects leading options and accepts `input.dvi [output.pdf]`.
- Derives default output name by replacing `.dvi` with `.pdf`.
- Runs `dvips -q -f "$infile"` and pipes to Ghostscript with `-dNOPAUSE -dBATCH -sDEVICE=pdfwrite`.
- Passes options before and after fixed Ghostscript options so `-I` search paths take effect early.

Filesystem relevance:
- External conversion pipeline over named input/output files; no filesystem internals.
