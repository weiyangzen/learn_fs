# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalphac.c

Purpose: Implements Ghostscript alpha-compositing objects, default compositor device, color packing/unpacking, rectangle compositing, and the per-pixel compositing operation engine.

Key interfaces: `gs_composite_alpha_type`, `gs_create_composite_alpha`, compositor serialization/deserialization helpers, device procedures for alpha compositor forwarding, and `composite_values`.

Control flow: composite objects store operation and optional dissolve delta. `composite_Copy` bypasses wrapping; other ops create a forwarding device that reads target rows into standard chunky alpha-capable form, composites a constant fill source over destination rows via `composite_values`, then writes changed rows back. Color mapping uses premultiplied alpha. `composite_values` handles alpha-first/alpha-last/no-alpha layouts, constant or data-backed sources, bit depths, and operators such as Clear, Copy, source/destination over/in/out/atop, XOR, PlusD, PlusL, Highlight, and Dissolve.

Dependencies: Uses Ghostscript compositor/device framework, `gxgetbit` sample load/store macros, `gxalpha`, `gxcomp`, `gxlum`, image alpha enums, and reference-counted allocation.

Risks and notes: Comments mark implementation as simple and inefficient. Some device operations (`copy_mono`, `copy_color`, `copy_alpha`) temporarily fall back to defaults. Fill path has an explicit “doesn't handle CMYK” note for extracting constant RGBA values, even though depth selection includes a CMYK case.
