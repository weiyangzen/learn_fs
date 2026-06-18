# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath.h

Public/internal fixed-point path and clipping-path API for Ghostscript imager code. The interface operates in device coordinates and uses fixed-point values rather than user-space floating-point values.

Key contents:
- Defines path insideness rules, segment notes, path copy options, and rectangle-classification enum.
- Declares path allocation/initialization/free/assignment functions for heap, contained, and local paths, including shared segment variants.
- Declares constructors for points, relative points, lines, rectangles, curves, partial arcs, path append, charpath append, closepath, and pop-close.
- Exposes state flags, current point, bbox queries, curve/void/null tests, rectangle detection, path reduction/copy/reversal/translation/scaling, dash expansion, and contour merging.
- Declares path enumeration functions that do not copy the path and expose segment notes/backtracking.
- Declares clipping path allocation, assignment, construction, intersection, conversion to path, rectangle inclusion, and enumeration APIs.

Notable dependencies:
- `gscpm.h`, `gslparam.h`, `gspenum.h`, and `gsrect.h`.
- Concrete structures are opaque here and defined in `gzpath.h`.

Research notes:
- The comments are an important ownership guide: path objects may be stack, heap, or embedded, while segment data are shared reference-counted objects.
- The copy options show the path subsystem supports flattening, monotonization, stroke-aware flattening, accurate tangents, and small-curve constraints.
