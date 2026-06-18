# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/pphs

Shell wrapper for printing the Primary Hint Stream from a linearized PDF.

Behavior:
- Runs Ghostscript quiet, no-display, with `pphs.ps "$@"`.
- Intended output is stdout.

Filesystem relevance:
- PDF inspection wrapper only.
