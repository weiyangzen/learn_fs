# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwreg.h

## Role
Header for Win32 Ghostscript application registry helpers.

## Contents
- Declares `win_get_reg_value` and `win_set_reg_value` for named registry values.

## Important Interfaces
- `int win_get_reg_value(const char *name, char *ptr, int *plen)`.
- `int win_set_reg_value(const char *name, const char *value)`.

## Dependencies And Coupling
- Implementation in `dwreg.c`.
- Return semantics align with Ghostscript environment lookup conventions.

## Risks And Notes
- Minimal API; caller supplies buffer length pointer for reads.

## Filesystem Relevance
None.
