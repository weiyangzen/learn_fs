# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath.h

`gxpath.h` is the public fixed-point path and clipping-path interface for Ghostscript internals. It operates in device coordinates using fixed-point values, not user-space floating-point coordinates.

It declares `gx_path`, insideness rules, segment-note flags, memory-management functions, path constructors, state-flag accessors, path accessors, path transformers, enumerators, and clipping-path APIs. Memory management mirrors the implementation in `gxpath.c`: paths may be heap, contained, or stack objects, and segment storage may be shared until a constructor unshares it.

Constructor declarations include `gx_path_new`, point/line/rectangle/curve/arc/path append operations, charpath handling, and closepath variants. Compatibility macros provide note-less versions. `gx_path_copy_options` controls flattening/monotonizing behavior used by `gx_path_copy_reducing`.

Accessors expose current point, bbox, subpath start, curve presence, null/void checks, rectangular detection, and curve suitability checks. Transformers include reducing copy, reverse copy, translation, power-of-two scaling, dash expansion, and merge-contacting-contours optimization.

The clipping-path section declares analogous allocation/assignment APIs plus constructors, intersection, rectangle tests, and enumeration. This header is a major integration contract for fill, stroke, clip, font, and shading code.
