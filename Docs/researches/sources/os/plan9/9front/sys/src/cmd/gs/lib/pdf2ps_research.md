# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/pdf2ps

Shell wrapper converting PDF to PostScript with Ghostscript.

Behavior:
- Collects leading `-?*` options.
- Accepts `input.pdf [output.ps]`; defaults output to basename `.ps`.
- Runs Ghostscript with `-dNOPAUSE -dBATCH -dSAFER -sDEVICE=pswrite`.
- Includes an initial `save pop` to reduce font flushing between pages.
- Repeats options before and after fixed options for search-path behavior.

Filesystem relevance:
- Conversion wrapper only.
