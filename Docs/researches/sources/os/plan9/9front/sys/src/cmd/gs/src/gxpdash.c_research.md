# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpdash.c

Dash expansion for flattened paths. It converts dashed stroke input into explicit path segments before stroking/filling.

Key behavior:
- `gx_path_add_dash_expansion` copies the path unchanged when no dash pattern is active; otherwise it expands each subpath.
- `subpath_expand_dashes` walks line-only subpaths, tracks dash index, remaining element length, and ink-on state.
- Segment lengths are measured in user space by inverse distance-transforming device-space fixed deltas.
- Dash-adapt mode rescales the dash pattern to fit an integer number of repetitions on a segment.
- Closed paths with initial ink require wraparound handling: the initial region may be skipped and emitted after the rest of the subpath.
- Degenerate segments are skipped unless round line caps are active.
- Near-end off dashes are stretched by epsilon to produce a dot when required.

Notable dependencies:
- Line state from `gsline.h`/`gzline.h`.
- Coordinate transforms from `gsmatrix.h` and `gscoord.h`.
- Concrete paths from `gzpath.h`.

Research notes:
- The implementation assumes the input path contains no curves.
- The `drawing` state is compact but subtle: `-1` skips initial closed-path segments, `0` draws normally, and `1` emits the delayed wraparound portion.
