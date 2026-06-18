# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/ps2ascii

Shell wrapper extracting ASCII text from PostScript through Ghostscript `ps2ascii.ps`.

Behavior:
- Installs a trap removing `_temp_.err` and `_temp_.out`.
- Uses Ghostscript options `-q -dNODISPLAY -dSAFER -dDELAYBIND -dWRITESYSTEMDICT -dSIMPLE`.
- With no arguments, acts as stdin-to-stdout filter.
- With one argument, reads that file and writes stdout.
- With two or more arguments, writes output redirected to the second path.

Filesystem relevance:
- Text extraction wrapper over PostScript input; no filesystem internals.
