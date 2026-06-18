# File Research: sources/os/plan9/9front/sys/src/9/port/mkrootall

Multi-file root embedding helper that emits assembly data for each boot file.

Key responsibilities:
- Requires argument triples: `name cname file`.
- Copies each file to a temporary output.
- Strips executable files except `venti`, which intentionally keeps its symbols.
- Runs `aux/data2s <cname>` for each file.
- Removes the temporary file on exit.

Role:
- Produces assembly data symbols consumed by `mkrootc`-generated `bootlinks()`.
