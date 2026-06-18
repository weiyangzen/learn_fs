# File Research: sources/os/bsd/netbsd-src/lib/lua/libm/libm.c

## Summary
Exposes many `math.h` functions and constants as a Lua module named `libm`.

## Main Responsibilities
- Use macros to generate wrappers for `double(double)`, `double(double,double)`, `double(int,double)`, and boolean numeric predicates.
- Provide special wrappers for `fma`, `nan`, `scalbn`, and `ilogb`.
- Validate Lua numeric or integer arguments before calling libm.
- Push results as Lua numbers, integers, or booleans.
- Export common constants such as `M_PI`, `M_E`, and related logarithm/square-root constants.

## Key Interfaces
- `luaopen_libm(lua_State *L)`.
- Lua functions include trigonometric, hyperbolic, exponential, logarithmic, Bessel, rounding, classification, and remainder functions.

## Risks
Argument validation is minimal and all conversion uses Lua number/integer APIs. Platform-specific availability is visible through `#ifndef __vax__` for `nextafter`.
