# File Research: sources/os/bsd/dragonflybsd/sys/sys/syslimits.h

BSD/POSIX system limit constants.

Key contents:
- Defines fixed limits including:
  - `ARG_MAX` 262144
  - `CHILD_MAX` 40
  - `LINK_MAX` 32767
  - `MAX_CANON`/`MAX_INPUT` 255
  - `NAME_MAX` 255
  - `NGROUPS_MAX` 16
  - `OPEN_MAX` 64
  - `PATH_MAX` 1024
  - `PIPE_BUF` 512
  - `IOV_MAX` 1024
- Warns userland when included directly outside expected headers.
- Leaves `HOST_NAME_MAX` undefined so applications use conservative values or `sysconf()`.

Important behavior:
- Header comments explicitly discourage adding new variables here.
- Some values are conditionally defined only if not already provided.

Research notes:
- This is user-visible ABI/standards surface.
- The intentionally undefined limits are as important as the defined constants.
