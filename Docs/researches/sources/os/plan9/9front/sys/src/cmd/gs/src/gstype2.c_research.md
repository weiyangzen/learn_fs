# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype2.c

Implements Ghostscript's Adobe Type 2 charstring interpreter on top of the Type 1 font/hinting machinery.

Key behavior:
- Initializes Type 1 hinter state for Type 2 charstrings, including CTM/font-matrix mapping, font data, grid-fitting flags, and delayed width/origin setup.
- Parses encrypted or unencrypted Type 2 charstring bytes into fixed-point operand-stack values, including 1-byte, 2-byte, 4-byte, and `shortint` encodings.
- Handles Type 2 drawing operators: moves, lines, alternating horizontal/vertical lines, cubic curves, curve-line/line-curve forms, flex operators, and `endchar`.
- Handles hints through `hstem`, `vstem`, `hstemhm`, `vstemhm`, `hintmask`, and `cntrmask`; hint masks are parsed according to the accumulated stem count.
- Implements local/global subroutine calls with Type 2 biasing, saving interpreter state across subroutine frames and freeing glyph data on `return`.
- Supports Type 2 stack/arithmetic/storage operators such as `blend`, `store`, `load`, boolean operators, arithmetic, `put/get`, `ifelse`, `roll`, and transient-array access.
- Implements Type 2 `endchar` seac compatibility for 4/5 operand accented-character charstrings.

Dependencies:
- Depends on Type 1 state, path, hinting, fixed-point arithmetic, matrix/coordinate, and font data structures from `gxfont1.h`, `gxtype1.h`, `gxhintn.h`, `gxpath.h`, and related Ghostscript headers.
- Uses `gs_type1_*` helpers for side bearings, seac handling, initialization, and finalization.
- Uses `t1_hinter__*` calls for all path construction and hint-aware geometry emission.

Research notes:
- Registry support is effectively limited to a single fake registry item backed by `WeightVector`.
- Counter masks are parsed, but the `cntrmask` action is marked `NYI`.
- The Type 2 `random` operator is present but marked `NYI`.
- Out-of-range subroutine calls are deliberately ignored for Adobe PDF Library compatibility.
