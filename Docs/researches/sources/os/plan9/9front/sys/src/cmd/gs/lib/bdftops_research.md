# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/bdftops

Small Ghostscript shell wrapper for converting BDF font data through `bdftops.ps`.

Behavior:
- Defines install-time-substituted `GS_EXECUTABLE=gs`.
- Executes Ghostscript quietly with `-dBATCH -dNODISPLAY`.
- Passes `bdftops.ps` and all user arguments after `--`.

Filesystem relevance:
- Process launcher only; uses Ghostscript to read/write files named by arguments.
