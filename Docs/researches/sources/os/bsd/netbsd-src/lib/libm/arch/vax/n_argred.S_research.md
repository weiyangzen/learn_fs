# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_argred.S

## Scope

Provides hidden VAX helper entry points `__libm_argred` and `__libm_sincos` for `_sin`, `_cos`, and `_tan`. It implements Bob Corbett argument reduction and Peter Tang polynomial sine/cosine evaluation for VAX D-format doubles.

## APIs And Behavior

- `__libm_argred` reduces an input argument to `[-pi/4, pi/4]` and returns quadrant in `%r0`, reduced D-format value in `%r2/%r1`, extension in `%r3`, and sin/cos selector in `%r4`.
- Small arguments below the 29th `pi/2` table entry use table lookup against split `leading`, `middle`, and `trailing` multiples of `pi/2`.
- Large arguments call `trigred`, which extracts exponent/fraction bits, multiplies by a selected slice of `2/pi`, handles cancellation by generating extra bits, derives the quadrant, then converts product bits back to D-format plus F-format extension.
- `__libm_sincos` adjusts the quadrant for cosine, selects sine or cosine polynomial, uses coefficient tables, applies the low-order extension correction, and flips sign based on quadrant.
- Contains VAX-specific workarounds, including an 11/780 FPA `polyd` workaround for tiny sine-square inputs.

## Dependencies And Risks

- Consumed by `n_sincos.S` and `n_tan.S` via `jsb`.
- Relies on exact VAX D/F-format bit layout, register conventions, and table constants.
- Range-reduction correctness depends on the embedded `2/pi` bit table and cancellation handling.
