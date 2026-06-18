# File Research: sources/os/bsd/freebsd-src/sbin/routed/rtquery/Makefile

Build recipe for the `rtquery` routed diagnostic tool.

Key responsibilities:
- Builds program `rtquery`.
- Installs manual page `rtquery.8`.
- Places the tool in the `runtime` package.
- Links against `libmd` for MD5 support.
- Sets warning level default to `3` and disables array-bounds warning handling through `NO_WARRAY_BOUNDS`.
- Includes FreeBSD `bsd.prog.mk`.

Dependencies:
- Requires the FreeBSD bsd.prog.mk build system and MD library.

Notable risks:
- `NO_WARRAY_BOUNDS` suggests the source intentionally uses packet unions or flexible indexing patterns that may otherwise trigger compiler diagnostics.
