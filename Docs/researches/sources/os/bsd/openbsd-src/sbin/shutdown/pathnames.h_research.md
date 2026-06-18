# File Research: sources/os/bsd/openbsd-src/sbin/shutdown/pathnames.h

This header defines filesystem paths used by `shutdown`.

Key definitions:
- Includes `<paths.h>`.
- `_PATH_FASTBOOT`: `/fastboot`
- `_PATH_HALT`: `/sbin/halt`
- `_PATH_REBOOT`: `/sbin/reboot`
- `_PATH_WALL`: `/usr/bin/wall`
- `_PATH_RC`: `/etc/rc`

Integration:
- `shutdown.c` uses these paths for `unveil()`, fastboot marker creation, user broadcasts, halt/reboot execution, and rc shutdown scripts.

Risk notes:
- Path constants are part of the privileged shutdown flow and must match the base system layout.
