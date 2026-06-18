# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscoord.h

## Purpose
Public interface to graphics-state CTM and coordinate transformation procedures.

## Key Contents
- Declares CTM modification APIs: init/default/current/set matrix, translate, scale, rotate, concat.
- Declares extensions for default matrix and character matrix control.
- Declares point and distance transformation APIs.
- Forward-declares `gs_imager_state` and declares imager-state matrix helpers.

## Dependencies
Requires matrix and graphics-state types from `gsmatrix.h` and `gsstate.h`.

## Research Notes
Implementation is in `gscoord.c`.
