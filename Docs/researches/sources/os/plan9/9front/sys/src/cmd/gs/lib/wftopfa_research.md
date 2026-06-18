# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/wftopfa

Small Ghostscript wrapper for `wftopfa.ps`.

Behavior:
- Defines install-time-substituted `GS_EXECUTABLE=gs`.
- Executes Ghostscript quiet, no-display, with `wftopfa.ps "$@"`.

Filesystem relevance:
- Font conversion wrapper only.
