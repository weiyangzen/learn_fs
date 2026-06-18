# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsclipsr.c

## Role

`gsclipsr.c` implements Ghostscript `clipsave` and `cliprestore` operations by maintaining a reference-counted stack of saved clipping paths.

This is graphics-state clipping infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_clipsave`
- `gs_cliprestore`

## Core Behavior

`gs_clipsave` creates a shared copy of the current clip path, allocates a `gx_clip_stack_t`, initializes reference counting with `rc_free_clip_stack`, and pushes it onto `pgs->clip_stack`.

`gs_cliprestore` pops from `pgs->clip_stack` when present and restores the saved clip path. If the stack node is uniquely referenced, it frees the stack node and assigns the clip path with transfer of ownership; otherwise it preserves the shared clip path and decrements the stack reference count.

If no clip stack is present, `cliprestore` falls back to restoring the clip path from the saved graphics state.

## Memory Management

`rc_free_clip_stack` frees stack nodes iteratively and frees each associated clip path, avoiding recursion through long clip-stack chains.

## Dependencies

Uses graphics state, clip path, path, fixed-coordinate, and Ghostscript GC/refcount support.

## Notable Risks

- `gs_clipsave` must handle partially failed allocation for either the clip-path copy or stack node; it does free both possible allocations on failure.
- `gs_cliprestore` assumes `pgs->saved` is valid when no explicit clip stack exists.
