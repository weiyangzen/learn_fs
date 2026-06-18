# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/frame.c

Changes the active plotting frame within the base frame.

Key responsibilities:
- Computes new `left`, `bottom`, `sidex`, and `sidey` from fractional frame coordinates.
- Adjusts current scales according to the frame-size change.
- Recomputes `quantum` from the base environment.

Notable behavior:
- Uses `e0` as the immutable base frame and modifies `e1`.
- Enforces a minimum `quantum` of `.01`.

Notable risks:
- Does not validate `xf > xs` or `yf > ys`; inverted or zero frames can produce odd scaling.
