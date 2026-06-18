# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/floor1.c

Vorbis floor backend 1 implementation, including setup serialization, decode reconstruction, and encoder curve fitting.

Important routines:
- `floor1_pack()` writes partitions, class definitions, subclass books, multiplier, and post list.
- `floor1_unpack()` reads and validates floor1 setup, including class/subbook indexes, post count bounds, and duplicate post positions.
- `floor1_look()` precomputes sorted post indexes, reverse indexes, quantization range, and low/high prediction neighbors.
- `render_point()`, `render_line()`, and `render_line0()` perform integer line interpolation and floor curve rendering.
- `accumulate_fit()`, `fit_line()`, and `inspect_error()` build weighted least-squares fits against log MDCT/masking curves for encoder floor approximation.
- `floor1_fit()` greedily splits floor segments where interpolation exceeds error bounds, producing post values for encoding.
- `floor1_interpolate_fit()` creates intermediate bitrate-managed floor fits.
- `floor1_encode()` quantizes posts, writes prediction residuals through codebooks, and renders an integer mask.
- `floor1_inverse1()` decodes floor post values and unwraps prediction residuals.
- `floor1_inverse2()` renders the decoded floor envelope into the spectral output.
- `floor1_exportbundle` registers pack/unpack/look/free/inverse hooks.

Important data:
- `FLOOR1_fromdB_LOOKUP[256]` converts quantized floor dB values to linear multipliers.
- `lsfit_acc` stores weighted sums for line fitting.

Integration points:
- `mapping0_forward()` directly calls `floor1_fit()`, interpolation, and `floor1_encode()` for encoder work.
- `mapping0_inverse()` calls floor backend hooks to recover envelope curves before MDCT inverse.
- `info.c` uses the backend registry to pack/unpack floor setup.

Risk and review signals:
- Contains an `exit(1)` in `floor1_fit()` if internal fit state reaches an impossible neighbor case; this is hostile in library-style code.
- Many codec bounds are explicitly checked during unpack, especially post counts and codebook indexes.
- Encoder fit quality is tuning-sensitive; tests should cover zero floors, duplicate/invalid postlists, malformed packet EOF, and managed bitrate floor interpolation.
- Decode clamps rendered floor lookup indexes to `[0,255]`.

Filesystem relevance:
- No filesystem logic. This is Vorbis spectral envelope codec logic.
