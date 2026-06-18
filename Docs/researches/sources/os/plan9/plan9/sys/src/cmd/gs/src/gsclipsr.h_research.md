# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsclipsr.h

## Purpose
Small public interface for `clipsave` and `cliprestore`.

## Key Contents
- Declares `gs_clipsave(gs_state *)`.
- Declares `gs_cliprestore(gs_state *)`.

## Dependencies
Assumes `gs_state` is already declared by the including context.

## Research Notes
The implementation is entirely in `gsclipsr.c`.
