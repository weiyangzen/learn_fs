# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/gsnd

Minimal Ghostscript no-display wrapper.

Behavior:
- Defines install-time-substituted `GS_EXECUTABLE=gs`.
- Executes `$GS_EXECUTABLE -dNODISPLAY "$@"`.

Filesystem relevance:
- Process wrapper only.
