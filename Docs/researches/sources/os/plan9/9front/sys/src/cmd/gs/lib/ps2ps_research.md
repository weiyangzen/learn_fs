# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/ps2ps

Shell wrapper that distills PostScript to PostScript using Ghostscript `pswrite`.

Behavior:
- Starts options with `-dSAFER`, appends leading options, requires `input.ps output.ps`.
- Prints usage with an example when arguments are wrong.
- Runs Ghostscript quiet with `-sDEVICE=pswrite`, output file, `-dNOPAUSE -dBATCH`, options, and input.

Filesystem relevance:
- Conversion wrapper only.
