# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/82-gfs2-withdraw.rules.in

udev rule template for GFS2 withdraw events.

Behavior:
- On `SUBSYSTEM=="gfs2"` and `ACTION=="offline"`, it runs `/bin/sh @libexecdir@/gfs2_withdraw_helper`.

Research notes:
- `@libexecdir@` is replaced by `gfs2/scripts/Makefile.am`.
