# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalphac.c

Purpose: Alpha-compositing implementation for Ghostscript.

Composite objects: Defines `gs_composite_alpha_type`, `gs_composite_alpha_t`, object equality, serialization, deserialization, and `gs_create_composite_alpha`. `composite_Dissolve` stores an extra float `delta`; other operations serialize as a one-byte opcode.

Compositor device: `c_alpha_create_default_compositor` returns the original target for `Copy`, otherwise creates a forwarding alpha-composite device with chunky 8-bit component storage plus alpha. It forwards most device procedures but overrides color mapping, fill rectangle, copy operations, and close.

Color and rendering path: RGB/RGBA mapping uses premultiplied alpha. `dca_fill_rectangle` reads each target row through `get_bits_rectangle` in a standard representation, composites a constant source color into that row with `composite_values`, then writes back via `copy_color` when a copy buffer was used.

Core compositing: `composite_values` handles 1-4 color components plus optional first/last alpha, variable source/destination bits per value, constant or data-backed sources, and operators Clear, Copy, Sover, Sin, Sout, Satop, Dover, Din, Dout, Datop, Xor, PlusD, PlusL, Highlight, and Dissolve. It rejects operations that can produce non-unity alpha when the destination has no alpha channel.

Dependencies and notes: Uses image sample load/store macros, `gx_device` forwarding, `gxgetbit` row access, and luminance weights. Several comments mark temporary/default implementations for copy paths and incomplete CMYK handling in rectangle fills.
