# File Research: sources/os/bsd/netbsd-src/lib/libc/Makefile

Top-level NetBSD libc build file.

Key behavior:
- Includes `Makefile.inc`, sets `LIB=c`, and adds libc include paths.
- Includes architecture-specific `Makefile.inc` and generates `assym.h` from `genassym.cf` when present.
- Supports `BUILD_LEGACY=yes` as separate compat library; otherwise includes compat code in libc and defines `__BUILD_LEGACY`.
- Includes many subsystem make fragments: common libc, atomic, db, citrus, compat, compiler_rt, dlfcn, gdtoa, gen, gmon, inet, locale, resolver, stdio, stdlib, string, sys, uuid, yp, and others.
- Removes C sources shadowed by architecture assembly implementations and adds lint C versions to `LSRCS`.
- Generates sorted tags for non-multilib, non-rumprun builds.
- Sets shared-library flags for dynamic ctype/I18N behavior and `-z initfirst`.

Dependencies:
- NetBSD make infrastructure and the full libc source tree.

Notes:
- The source de-duplication logic is important for architecture assembly overrides and lint coverage.
