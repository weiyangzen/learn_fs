# File Research: sources/os/bsd/openbsd-src/sbin/mountd/pathnames.h

Purpose: Defines mountd-specific filesystem paths.

Constants:
- `_PATH_EXPORTS`: `/etc/exports`, default export configuration.
- `_PATH_RMOUNTLIST`: `/var/db/mountdtab`, persistent remote mount list.
- `_PATH_MOUNTDPID`: `/var/run/mountd.pid`, daemon pid file.

Integration:
- Included by `mountd.c`.
- Works with `<paths.h>` but only adds mountd-specific paths.
