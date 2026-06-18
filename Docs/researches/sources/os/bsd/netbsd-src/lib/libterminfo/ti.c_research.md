# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/ti.c

Capability accessor implementation for terminfo APIs.

Key responsibilities:
- Implements explicit-terminal accessors:
  - `ti_getflag`
  - `ti_getnum`
  - `ti_getstr`
- Implements global wrappers using `cur_term`:
  - `tigetflag`
  - `tigetnum`
  - `tigetstr`
- Uses generated capability index functions:
  - `_ti_flagindex`
  - `_ti_numindex`
  - `_ti_strindex`
- Falls back to user-defined capabilities stored in `TERMUSERDEF`.

Return behavior:
- Absent booleans return `ABSENT_BOOLEAN`.
- Invalid or absent numerics normalize to `ABSENT_NUMERIC`.
- Unknown numeric/string capabilities return cancelled sentinels where appropriate.

Role in subsystem:
- Runtime API layer for querying loaded terminal capabilities.
