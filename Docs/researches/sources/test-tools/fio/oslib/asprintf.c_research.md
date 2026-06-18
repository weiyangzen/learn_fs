# sources/test-tools/fio/oslib/asprintf.c

Purpose: fallback implementations of GNU `vasprintf()` and `asprintf()` for platforms lacking them.

Important APIs/functions: under `!CONFIG_HAVE_VASPRINTF`, `vasprintf()` computes required length using a copied `va_list`, allocates the buffer, stores it in `*strp`, and formats into it. Under `!CONFIG_HAVE_ASPRINTF`, `asprintf()` wraps `vasprintf()` with `va_start()`/`va_end()`.

Control flow and state: no persistent state. Allocation failure returns `-1`; `vsnprintf()` errors propagate.

Dependencies and integration: includes `oslib/asprintf.h`; used by other fio portability code such as Linux zoned-device sysfs path construction.

Risks: `*strp` is assigned even on allocation failure as `NULL`. The fallback assumes `vsnprintf(NULL, 0, ...)` is supported by the C library. Callers own the returned allocation.

Test signals: build on systems without native `asprintf`, format strings with zero-length, long, and invalid conversions, and verify allocation ownership.
