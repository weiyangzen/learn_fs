# File Research: sources/os/plan9/plan9/sys/src/9/pc/nomtrr.c

Stub implementation used when MTRR support is excluded.

Key elements:
- `mtrr` raises `error("mtrr support excluded")`.
- `mtrrprint` returns 0.

Interactions:
- Satisfies the same external interface as `mtrr.c`.
- Callers such as `screen.c` may wrap `mtrr` in `waserror` to harmlessly continue.

Research notes:
- Build-time alternative only; no hardware behavior.
