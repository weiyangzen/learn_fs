# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsha.c

Provides the default linear-color scanline fill procedure used by shading fallback paths.

`gx_default_fill_linear_color_scanline` receives a scanline span, starting component colors, fractional gradient state, gradient numerators, and denominator. It walks pixels left to right, incrementally updates each component, encodes component values into a `gx_color_index` using the device’s `comp_shift` and `comp_bits`, and groups consecutive pixels with identical encoded color into rectangle fills.

The function honors clipping and supports `swap_axes`, emitting either horizontal rectangles or transposed vertical rectangles through the device `fill_rectangle` proc. It also emits visual-debug rectangle traces through `vd_rect`.

Dependencies are the device color-info bit layout initialized by separable/linear color setup and default rectangle fill support.

Risks: this fallback assumes meaningful `comp_shift`/`comp_bits` for the target device. It is correct but potentially slow because it decomposes gradients into many constant-color rectangles rather than writing pixels directly.
