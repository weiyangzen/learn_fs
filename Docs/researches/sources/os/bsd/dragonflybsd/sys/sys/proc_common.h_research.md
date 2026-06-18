# File Research: sources/os/bsd/dragonflybsd/sys/sys/proc_common.h

Shared process and LWP state enum definitions.

Key responsibilities:
- Defines `enum lwpstat` values:
  - `LSRUN`
  - `LSSTOP`
  - `LSSLEEP`
- Defines `enum procstat` values:
  - `SIDL`
  - `SACTIVE`
  - `SSTOP`
  - `SZOMB`
  - `SCORE`

Important behavior:
- Kept separate so process-state enums can be shared by process-related headers without pulling in full `proc.h`.

Dependencies:
- No includes beyond guard.

Notable risks:
- Numeric enum values are visible through kernel structure consumers and diagnostic tools.
