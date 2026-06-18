# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priocntl.h

## Purpose
Defines the `priocntl(2)` and `priocntlset(2)` scheduling-control ABI, command codes, class/parameter structures, varargs parameter format, and 32-bit compatibility forms.

## Main Interfaces
- `PC_VERSION`
- User functions:
  - `priocntl()`
  - `priocntlset()`
- Commands:
  - `PC_GETCID`, `PC_GETCLINFO`, `PC_SETPARMS`, `PC_GETPARMS`
  - `PC_ADMIN`, `PC_GETPRIRANGE`
  - `PC_DONICE`, `PC_SETXPARMS`, `PC_GETXPARMS`
  - `PC_SETDFLCL`, `PC_GETDFLCL`, `PC_DOPRIO`
- Class metadata:
  - `PC_CLNULL`
  - `PC_CLNMSZ`
  - `PC_CLINFOSZ`
  - `PC_CLPARMSZ`
  - `pcinfo_t`
  - `pcparms_t`
- Nice/priority:
  - `PC_GETNICE`, `PC_SETNICE`, `pcnice_t`
  - `PC_GETPRIO`, `PC_SETPRIO`, `pcprio_t`
- Extended varargs:
  - `PC_VAPARMCNT`
  - `PC_KY_NULL`
  - `PC_KY_CLNAME`
  - `pc_vaparm_t`
  - `pc_vaparms_t`
  - 32-bit packed variants where required.
- POSIX/admin structures:
  - `pcpri_t`
  - `pcadmin_t`
  - `pcadmin32_t`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/procset.h`. Used by scheduler classes, libc, `dispadmin`, and POSIX scheduling interfaces.

## Research Notes
Several command codes and structures are marked not for general use. Alignment-sensitive 32-bit translation is guarded by architecture alignment checks.
