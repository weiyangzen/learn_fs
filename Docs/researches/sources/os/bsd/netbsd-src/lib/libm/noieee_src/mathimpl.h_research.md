# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/mathimpl.h

Private support header for the old `noieee_src` libm implementation. It abstracts constant declarations for VAX/Tahoe versus IEEE targets and declares shared helper functions.

Key behavior:
- Defines `vc()` for VAX/Tahoe constants assembled from 16-bit chunks, with endian-specific concatenation.
- Defines `ic()` for IEEE constants as ordinary `double` values.
- Provides `_TINY`, `_TINYER`, and `_HUGE` constants tuned by target.
- Declares shared internal helpers: `__exp__E`, `__exp__D`, `__log__L`, `__log__D`, `infnan`, and `struct Double`.

Important dependencies: `<sys/cdefs.h>`, `<math.h>`, and `<stdint.h>`.

Notable risks:
- Many no-IEEE source files depend on `_LIBM_STATIC` or `_LIBM_DECLARE` being set before inclusion to choose storage class.
- The header exists to keep legacy non-IEEE formats working; constants and casts are intentionally target-sensitive.
