# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/xsize.h

Purpose: provides checked `size_t` arithmetic helpers for allocation-size calculations.

Important APIs/types/functions: `xcast_size_t`, `xsum`, `xsum3`, `xsum4`, `xmax`, and `xtimes` return `SIZE_MAX` as an overflow sentinel. `size_overflow_p` and `size_in_bounds_p` test that sentinel. Inline helpers carry GCC pure attributes where available.

State and persistence: no state.

Dependencies and integration: includes `stddef.h`, `limits.h`, and optionally `stdint.h`. Used by `printf-parse.c` and `vasnprintf.c` to avoid allocating undersized buffers after overflow.

Risks and test signals: callers must check `SIZE_MAX` before `malloc`; `xtimes` assumes positive element size and is a macro to handle wider integer inputs. Test boundary arithmetic near `SIZE_MAX`, multiplication overflow, and callers that propagate the sentinel into allocation failure paths.
