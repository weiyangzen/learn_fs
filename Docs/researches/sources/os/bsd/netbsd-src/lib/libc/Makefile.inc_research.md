# File Research: sources/os/bsd/netbsd-src/lib/libc/Makefile.inc

Shared libc build configuration.

Key behavior:
- Marks libc as unsanitized and installed in the shared library directory.
- Defines `RUMPRUN?=no`, `WARNS=5`, and libc-wide preprocessor flags `_LIBC`, `LIBC_SCCS`, `SYSLIBC_SCCS`, `_REENTRANT`, `_LIBC_INTERNAL`, `_DIAGNOSTIC`, and optionally `MLIBDIR`.
- Adds csu common include path.
- Enables `HESIOD`, `INET6`, `NLS`, and `YP` based on build options.
- Configures lint flags for C23, warning-as-error, and selected warning suppressions.
- Includes `libcincludes.mk`.
- Defines `ARCHDIR=${.CURDIR}/arch/${ARCHSUBDIR}` and adds it to assembler include paths.
- Disables recursive linting against libc itself by setting `LLIBS=`.

Dependencies:
- `<bsd.own.mk>` and libc include/install infrastructure.
