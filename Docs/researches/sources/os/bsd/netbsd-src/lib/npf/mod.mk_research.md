# File Research: sources/os/bsd/netbsd-src/lib/npf/mod.mk

## Summary
Shared build fragment for NPF extension modules.

## Main Responsibilities
- Sets warnings to 5 and disables lint.
- Builds each extension as a shared module with `LIBISMODULE=yes`.
- Installs modules under `/lib/npf` or machine-library-specific `/lib/${MLIBDIR}/npf`.
- Sets `LIB=${MOD}` and source file `npf${MOD}.c`.
- Links against `libnpf`.
- Includes `bsd.lib.mk`.

## Integration Notes
Each extension Makefile only needs to set `MOD`; this fragment derives the rest.
