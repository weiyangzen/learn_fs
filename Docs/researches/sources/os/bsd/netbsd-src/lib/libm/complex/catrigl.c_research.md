# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catrigl.c

## Scope

Long-double version of the modern inverse complex trig implementation, currently disabled behind `#ifdef notyet`.

## APIs And Behavior

- The disabled implementation mirrors `catrig.c` for long double, including long-double constants, `GET_LDBL_EXPSIGN`, `SET_LDBL_EXPSIGN`, `do_hard_work`, `casinhl`, `casinl`, `cacosl`, `cacoshl`, `catanhl`, and `catanl`.
- Disabled because of comments around missing `log1pl` / `__HAVE_LONG_DOUBLE` support.
- Active `#else` path aliases long-double functions to double implementations: `_casinl -> casin`, `_catanl -> catan`, `cacoshl -> cacosh`, `cacosl -> cacos`, `casinhl -> casinh`, and `catanhl -> catanh`.

## Dependencies And Risks

- Active behavior sacrifices true long-double implementation by aliasing to double variants.
- Disabled code contains endian/format assumptions for 80-bit extended long double.
