# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalpha.h

Purpose: Public API for alpha value in `gs_state`.

Exports: Declares `gs_setalpha(gs_state *, floatp)` and `gs_currentalpha(const gs_state *)`.

Dependencies and notes: The header is intentionally tiny so it can be included by state initialization code independently of the broader alpha-compositing feature.
