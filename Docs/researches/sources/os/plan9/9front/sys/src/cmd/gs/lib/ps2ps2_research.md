# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/ps2ps2

Shell wrapper that distills PostScript using Ghostscript `ps2write`.

Behavior:
- Same argument/options pattern as `ps2ps`, but emits with `-sDEVICE=ps2write`.
- Requires exactly `input.ps output.ps`.

Filesystem relevance:
- Conversion wrapper only.
