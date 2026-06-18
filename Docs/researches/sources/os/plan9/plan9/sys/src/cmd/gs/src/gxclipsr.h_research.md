# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipsr.h

## Purpose
Defines internals for clip save/restore stack management.

## Main Responsibilities
- Forward-declares `gx_clip_path` and `gx_clip_stack_t`.
- Defines `gx_clip_stack_s`, a reference-counted linked stack node.
- Provides GC structure descriptor macro `private_st_clip_stack`.

## Key Structure
`gx_clip_stack_s` contains:
- Reference-count header.
- Pointer to saved `gx_clip_path`.
- Pointer to next stack node.

## Dependencies
- Includes `gsrefct.h` for reference-counting support.

## Research Notes
The file explains that clipping paths are stacked separately from graphics-state objects because off-stack graphics states may share them. Reference counting is therefore required.
