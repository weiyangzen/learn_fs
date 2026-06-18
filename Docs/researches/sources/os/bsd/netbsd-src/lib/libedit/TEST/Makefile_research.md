# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/Makefile

This small makefile builds libedit test programs.

Key settings:
- `NOMAN=1`
- `PROG=wtc1 test_filecompletion`
- Adds `-I${.CURDIR}/..` so tests can include libedit internals.
- Links with `-ledit -ltermlib`.
- Adds `-DDEBUG` when `DEBUG` is defined.
- Includes `<bsd.prog.mk>`.

Integration:
- Builds interactive wide-character test coverage (`wtc1`) and file completion escaping tests (`test_filecompletion`).
