# File Research: sources/os/plan9/9front/sys/src/cmd/image/affinewarp.c

Applies affine transformations to a Plan 9 image read from stdin.

Key points:
- Builds a stack of transformation matrices from command-line operations:
  - `-s x y` scale
  - `-r θ` rotate degrees
  - `-t x y` translate
  - `-S x y` shear
- Options:
  - `-R` enables replicated source sampling.
  - `-q` enables smoothing.
  - `-p` processes output bands in parallel.
- Optional four numeric args set destination rectangle; otherwise source rectangle is used.
- Composes transformations in stack order using `mkxform`.
- Uses `mkwarp` and `memaffinewarp` to render to a transparent destination.
- Parallel mode splits destination rectangle by rows using `initworkrects` and forks workers with shared memory.

Dependencies and interactions:
- Uses shared image utility functions from `image/util.c` and prototypes from `fns.h`.
- Uses Plan 9 `geometry.h` matrices and memdraw warp functions.

Research relevance:
- A command-line image geometry transform tool exposing Plan 9 memdraw affine-warp primitives.
