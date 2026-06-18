# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdf2ps

Shell wrapper converting PDF to PostScript.

Behavior:

- Accumulates leading options.
- Accepts `input.pdf [output.ps]`, deriving the output name when omitted.
- Runs Ghostscript with `-sDEVICE=pswrite`, `-dNOPAUSE`, `-dBATCH`, `-dSAFER`, and an initial `save pop` to reduce font flushing between pages.
- Passes options both before and after fixed switches so include-path options can take effect early.

This is document conversion command glue.
