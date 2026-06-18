# File Research: sources/os/bsd/netbsd-src/sys/sys/syslimits.h

This public header defines system limit constants exposed under POSIX, X/Open, and NetBSD feature-test conditions.

Key interface details:
- Includes `<sys/featuretest.h>`.
- Optionally includes `opt_syslimits.h` for kernel option overrides.
- Defines core limits when POSIX/XOpen/NetBSD feature macros are active:
  - `ARG_MAX`, `CHILD_MAX`, `OPEN_MAX`
  - `GID_MAX`, `UID_MAX`
  - `LINK_MAX`, `NAME_MAX`, `PATH_MAX`
  - terminal and pipe limits such as `MAX_CANON`, `MAX_INPUT`, `PIPE_BUF`
- Defines POSIX.2 utility limits: `BC_*`, `COLL_WEIGHTS_MAX`, `EXPR_NEST_MAX`, `LINE_MAX`, `RE_DUP_MAX`.
- Defines realtime and X/Open gated limits such as `DELAYTIMER_MAX`, `LOGIN_NAME_MAX`, `IOV_MAX`, and `NZERO`.

Research notes:
- `PATH_MAX` is consumed by other headers in this group, notably `swap.h` and `sysctl.h`.
- `NAME_MAX` is documented as needing to stay in sync with `MAXNAMLEN`.
- This file is a portability contract for userland and kernel-adjacent code that uses standardized limits.
