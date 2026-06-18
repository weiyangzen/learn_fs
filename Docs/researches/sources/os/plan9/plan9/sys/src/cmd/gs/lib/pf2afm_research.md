# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pf2afm

Shell wrapper that makes an AFM file from PFB/PFA and optionally PFM font files.

It runs:

- `gs -q -dNODISPLAY -dSAFER -dDELAYSAFER -- pf2afm.ps "$@"`

The PostScript helper owns the actual font metric extraction. This file only selects the Ghostscript invocation.
