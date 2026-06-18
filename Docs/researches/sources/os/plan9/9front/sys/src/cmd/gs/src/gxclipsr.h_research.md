# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipsr.h

Defines the internal reference-counted stack nodes used for clipsave/cliprestore.

Key behavior:
- Forward-declares `gx_clip_path` and `gx_clip_stack_t`.
- Defines `gx_clip_stack_s` with a reference-count header, a saved clip-path pointer, and a next-stack pointer.
- Provides the private GC descriptor macro for tracing `clip_path` and `next`.

Dependencies:
- Includes `gsrefct.h` for reference-count support and depends on Ghostscript GC descriptor macros.

Research notes:
- The clipping path stack is separate from the graphics-state stack and reference-counted because off-stack graphics states may share clip stack nodes.
