# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/pfbtopfa

Shell wrapper converting binary Type 1 `.pfb` fonts to ASCII `.pfa`.

Behavior:
- Accepts `input.pfb [output.pfa]`; defaults output to input basename `.pfa`.
- Runs Ghostscript quiet, no-display, with `pfbtopfa.ps "$1" "$outfile"`.

Filesystem relevance:
- Font conversion wrapper only.
