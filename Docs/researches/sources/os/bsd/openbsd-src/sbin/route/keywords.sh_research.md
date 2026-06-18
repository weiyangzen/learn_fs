# File Research: sources/os/bsd/openbsd-src/sbin/route/keywords.sh

This shell script regenerates `keywords.h` from a literal keyword list.

Key behavior:
- Writes the keyword list to `_keywords.t1`, sorts it, uppercases it with `tr`, and pairs lower/upper forms into `_keywords.t2`.
- Emits the `struct keytab`, `enum K_*` constants, and `keywords[]` initializer into `keywords.h`.
- Uses `${AWK:-awk}` for generation.
- Removes temporary `_keywords.t1` and `_keywords.t2`.

Integration:
- The generated table is consumed by `route.c` through `keyword()` and `bsearch()`.
- The script comment warns that it requires modern awk.

Risk notes:
- Temporary files are written in the current directory with fixed names.
- The generated `$OpenBSD$` marker is intentionally generic, so committed `keywords.h` may carry its own expanded revision.
