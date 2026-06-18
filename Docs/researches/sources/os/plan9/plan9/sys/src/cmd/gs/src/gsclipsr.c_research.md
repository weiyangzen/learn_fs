# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsclipsr.c

## Purpose
Implements Ghostscript `clipsave` and `cliprestore`.

## Key Behavior
- Defines the clip-stack GC/free descriptor.
- `gs_clipsave` allocates a shared copy of the current clip path and pushes it onto `pgs->clip_stack`.
- `gs_cliprestore` restores the top saved clip path or, if the explicit clip stack is empty, restores from the saved graphics-state clip path.
- Frees clip stack entries iteratively to avoid recursion through deep stack chains.

## Important Details
- If a clip stack entry is uniquely referenced, restore uses `gx_cpath_assign_free`; otherwise it preserves the path and decrements the stack reference count.
- Allocation failure during `clipsave` frees any partially allocated objects before returning `VMerror`.

## Dependencies
Uses graphics state internals, clip-stack internals, clip-path allocation/assignment, fixed/path headers, and Ghostscript reference-count helpers.

## Research Notes
This is graphics-state stack management only. It has no filesystem relevance.
