# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrl.h

## Scope

Header declarations and constants for long-double Cephes complex helpers.

## APIs And Constants

- Declares `_cchshl`, `_redupil`, and `_ctansl`.
- Defines `M_PIL` and `M_PI_2L`.

## Dependencies And Risks

- Constants are used by long-double wrappers such as `cacosl` and `ctanl`.
