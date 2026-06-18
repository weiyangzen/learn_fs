# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/b_logl.c

This file provides the ld128 extended-precision helper `__log__D(long double x)`, returning a two-part `struct Double` approximation of `log(x)`.

It uses a 128-entry table of `log(Fj)` split into `logF_head` and `logF_tail`, plus a short polynomial over a tightly reduced argument. The reduction normalizes `x` with `frexpl`, chooses `F = 1 + j/128`, computes `u = 2f / (2F + f)`, and accumulates `m * log(2)`, table terms, and the polynomial correction.

The important implementation detail is the deliberate split result: `r.a` is rounded to float precision and `r.b` carries the residual. This is used by legacy BSD gamma code needing extra precision without a native wider floating type.

Dependencies include `math_private.h`, `union ieee_ext_u`, `LD80C`, `frexpl`, `ldexpl`, and `ilogbl`.
