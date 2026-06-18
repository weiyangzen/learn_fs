# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_compat.c

Provides binary compatibility for the old global `_res` resolver state when `__BIND_NOSTATIC` is not defined. It defines `struct __res_state _res` with optional static initialization and exposes:
- `__res_get_old_state()` returning `_res`,
- `__res_put_old_state()` copying a newer state back into `_res`.

`res_data.c` uses these hooks under `COMPAT__RES` so programs that modified `_res` directly before `res_init()` can still influence `_nres` initialization.
