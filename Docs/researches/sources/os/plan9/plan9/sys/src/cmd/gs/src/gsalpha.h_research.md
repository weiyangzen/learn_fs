# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalpha.h

Purpose: Public API header for reading and setting the graphics-state alpha value.

Key interfaces: `gs_setalpha(gs_state *, floatp)` and `gs_currentalpha(const gs_state *)`.

Integration: Kept small so state initialization code can include alpha access even in builds without full alpha compositing support.

Risks and notes: Does not define `gs_state`; it assumes surrounding Ghostscript headers provide the type.
