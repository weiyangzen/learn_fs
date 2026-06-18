# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc0.c

## Role

`gsfunc0.c` implements FunctionType 0 Sampled functions, including sample extraction, linear and cubic interpolation, cached Bezier-pole interpolation, monotonicity analysis, scaling, serialization, and initialization.

This is PDF/PostScript function evaluation infrastructure, not filesystem code.

## Main Interface

- `gs_function_Sd_init`
- `gs_function_Sd_free_params`

## Core Behavior

Sampled functions map `m` inputs through a sample table to `n` outputs.

Supported bits per sample:

- 1, 2, 4, 8, 12, 16, 24, 32

Supported interpolation orders:

- 1: multilinear
- 3: multicubic
- 0: defaults to 1

The implementation includes:

- bit-level sample readers for each supported sample width
- input domain clipping and encode mapping
- output decode/range clipping
- recursive linear interpolation
- recursive cubic interpolation
- optimized cached cubic interpolation using a `pole` array of Bezier coefficients
- monotonicity checks for shading decomposition and optimization
- serialized output of parameters and raw sampled data

## Internal Data

`gs_function_Sd_t` extends the generic function header with sampled parameters. Internal cached fields include:

- `pole`
- `array_step`
- `stream_step`
- `array_size`

`double_stub` marks uncached pole entries.

## Important Constraints

- Maximum plausible inputs and outputs are both 16.
- Some monotonicity paths support only up to 4 dimensions, and tensor monotonicity for cubic paths is limited further to 3 dimensions.
- One-input linear functions with small output count avoid the pole cache.

## Notable Risks

- Several allocation failure paths in `gs_function_Sd_init` return immediately after partial allocation without freeing the just-allocated function object or prior arrays.
- The cached interpolation code is complex and explicitly marked as temporary development technology in several macros/comments.
- Monotonicity analysis returns `limitcheck` for dimensions beyond implemented buffer limits.
- `Range` is assumed present in cached cubic evaluation and clamping paths, consistent with Type 0 requirements but important for callers.
