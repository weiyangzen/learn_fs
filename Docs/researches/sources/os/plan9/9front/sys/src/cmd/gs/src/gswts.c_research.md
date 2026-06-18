# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gswts.c

Implements Well Tempered Screening cell selection, screen enumeration, threshold sorting, and screen conversion.

Key behavior:
- Defines two internal cell-parameter variants: Screen H for near-axis/45-degree optimized cells and Screen J for general-angle cells with probabilistic jumps.
- Uses integer-vector arithmetic, a 3-vector GCD-like reduction, cross products, and modular normalization to find compact repeating screen bases.
- Converts requested halftone frequency/angle and device matrix into `ufast/vfast/uslow/vslow` screen-space increments.
- Chooses Screen H cell dimensions with rational approximation and split-cell probabilities.
- Chooses Screen J dimensions by scanning candidate widths/heights, scoring geometric error, jump probabilities, memory usage, and cache penalties.
- Builds enumerators that expose current points in normalized `[-1,1]` spot-function coordinates and accept sampled spot values.
- Provides `wts_sort_cell`, a simple threshold-value sort, and `wts_sort_blue`, a BlueDot-inspired sort using a Gaussian bump to reduce clustering.
- Converts completed enumerators into runtime `wts_screen_t` structures for Screen H or Screen J.
- Includes a `UNIT_TEST` mode that emits a PGM threshold image from a square-dot spot function.

Dependencies:
- Uses Ghostscript halftone state (`gsht.h`), matrix/state types, fractional constants, and WTS runtime structures from `gxwts.h`.
- Uses standard `malloc/free/qsort` rather than Ghostscript GC memory for its working structures.

Research notes:
- Landscape and mirrored coordinate systems are explicitly listed as a todo in cell-size selection.
- Blue bump generation notes that anisotropic scaling could be handled more intelligently.
- `gs_wts_free_enum` and `gs_wts_free_screen` free only the outer structure, while allocations for cell/sample buffers are owned by fields inside those structures; this is notable for lifetime review.
