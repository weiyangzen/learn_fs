# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lune.c

Implements a conformal lune projection.

Key functions:
- `lune(double lat, double theta)` initializes east/west pole reference points, checks stereographic symmetry, sets scale and exponent.
- `Xlune()` maps via stereographic projection and a complex power transform:
  `w = ((1+z)^A - (1-z)^A) / ((1+z)^A + (1-z)^A)`.

Behavior notes:
- Rejects points below the configured east-pole latitude cap.
- Uses `Xstereographic`, `cpow`, and `cdiv`.
- Comments document branch cuts from east/west poles to south pole; without a cut routine, the code rejects outside a polar cap.
- Uses old-style implicit `int` return for `static Xlune`.
