# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptov.c

Provides signed `vlong` conversion helpers `vtomp(vlong v, mpint *b)` and `mptov(mpint *b)`. It mirrors `mptouv.c` but preserves sign in `vtomp` and saturates signed output in `mptov`.

`vtomp` allocates or resizes for `VLDIGITS`, clears the destination, records `sign = -1` for negative inputs, converts the absolute value into low-to-high limbs, and sets `top` to the number of emitted limbs.

`mptov` normalizes the input, returns `MAXVLONG` or `MINVLONG` on too many limbs depending on sign, reconstructs the magnitude, then clamps to signed bounds. Negative in-range values are returned as `-(vlong)v`; values beyond `MINVLONG` magnitude clamp to `MINVLONG`.
