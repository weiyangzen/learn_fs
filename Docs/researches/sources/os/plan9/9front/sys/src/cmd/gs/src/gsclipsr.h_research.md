# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsclipsr.h

## Role

`gsclipsr.h` declares the client interface for Ghostscript clipping save/restore operations.

This is graphics-state infrastructure, not filesystem code.

## Public API

- `gs_clipsave(gs_state *)`
- `gs_cliprestore(gs_state *)`

## Dependencies

Requires `gs_state` to be visible to callers through the surrounding Ghostscript headers.

## Notable Risks

No internal state is defined here; correctness is in `gsclipsr.c`.
