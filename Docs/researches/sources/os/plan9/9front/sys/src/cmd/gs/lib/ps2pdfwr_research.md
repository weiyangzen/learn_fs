# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/ps2pdfwr

Core Ghostscript wrapper for PostScript/EPS to PDF conversion without hardcoding compatibility level.

Behavior:
- Starts options with `-dSAFER` and appends leading `-?*` options.
- Accepts `(input.[e]ps|-) [output.pdf|-]`.
- Derives default output from `.eps`, `.ps`, or basename; stdin maps default output to stdout `-`.
- Runs Ghostscript quiet with `-dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=...`, repeats options for `-I`, calls `.setpdfwrite`, and reads the input file.

Filesystem relevance:
- Conversion wrapper; no filesystem implementation behavior.
