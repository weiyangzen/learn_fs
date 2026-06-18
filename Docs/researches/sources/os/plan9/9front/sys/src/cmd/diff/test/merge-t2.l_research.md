# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/merge-t2.l

Merge regression fixture with one deletion.

Key behavior:
- Contains `1` through `6`, then `8`, `9`, `10`.
- Omits line `7`.

Research notes:
- Useful for deletion-vs-deletion or deletion-vs-context merge cases.
