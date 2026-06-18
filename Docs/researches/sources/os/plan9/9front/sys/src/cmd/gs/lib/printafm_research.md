# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/printafm

Very small shell wrapper for printing AFM font metrics via Ghostscript.

Behavior:
- Executes `gs -q -dNODISPLAY -- printafm.ps "$@"`.
- Unlike neighboring wrappers, it directly uses `gs` rather than `GS_EXECUTABLE`.

Filesystem relevance:
- Font metric inspection wrapper only.
