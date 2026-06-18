# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/pf2afm

Shell wrapper for producing AFM metrics from PFA/PFB and optional PFM data via Ghostscript `pf2afm.ps`.

Behavior:
- Runs Ghostscript quiet, no-display, safer modes, then `pf2afm.ps "$@"`.
- Comments state output goes to `fontfilename.afm` and must not already exist.

Filesystem relevance:
- Font conversion wrapper only.
