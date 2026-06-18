# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pphs

Shell wrapper for printing the Primary Hint Stream from a linearized PDF.

It sets `GS_EXECUTABLE=gs` and executes:

- `gs -q -dNODISPLAY -- pphs.ps "$@"`

Output goes to stdout. The actual parsing is in `pphs.ps`.
