# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_scalbn.S

## Scope

Implements VAX `scalbn`, `ldexp`, and float/long-double aliases by adjusting D/F-format exponents.

## APIs And Behavior

- Weak aliases connect `scalbn`, `scalbnf`, `scalbnl`, `ldexp`, `ldexpf`, and `ldexpl` to internal entries.
- `_scalbnf` converts a float argument to double format and shares the double exponent path.
- `_scalbnl` strongly aliases to `_scalbn`.
- Checks exponent shift bounds before modifying the exponent field.
- Zero input remains zero; reserved operands return unchanged.
- Underflow returns signed zero via `copysign`; overflow calls `infnan(ERANGE)` and preserves input sign if it returns.

## Dependencies And Risks

- Depends on VAX exponent-field extraction/insertion with `extzv` and `insv`.
- Uses `infnan` for overflow signalling.
- Bound constants include guard margin around VAX exponent range and precision.
