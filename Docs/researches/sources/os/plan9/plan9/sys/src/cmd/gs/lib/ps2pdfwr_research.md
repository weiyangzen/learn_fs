# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdfwr

Core shell wrapper for PostScript/EPS-to-PDF conversion without setting a compatibility level itself.

Behavior:

- Defaults options to `-dSAFER` and appends leading switches.
- Accepts `(input.[e]ps|-) [output.pdf|-]`.
- Derives the output name from `.eps`, `.ps`, or the full basename when omitted; preserves `-` for stdin/stdout-style usage.
- Runs Ghostscript with `-q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=...`, repeats options, calls `.setpdfwrite`, and reads the input with `-f`.

PDF-version wrappers `ps2pdf12`, `ps2pdf13`, and `ps2pdf14` call this script with `-dCompatibilityLevel`.
