# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/sqrt.c

Square-root layout for `eqn`.

Key behavior:
- Estimates radical glyph size from enclosed box height and device type.
- Updates result height and emits troff strings for radical and overbar.
- Uses width measurement of enclosed box and font-size changes.

Filesystem relevance:
- Typesetting layout only.
