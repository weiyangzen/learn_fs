# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/Makefile.am

Automake packaging for GFS2 helper scripts and udev rule generation.

Installs:
- `gfs2_lockcapture` and `gfs2_trace` as `dist_sbin_SCRIPTS`
- `gfs2_withdraw_helper` as `dist_libexec_SCRIPTS`
- Generated `82-gfs2-withdraw.rules` into `@udevdir@/rules.d`

Build rule:
- Generates `82-gfs2-withdraw.rules` from `.in` by replacing `@libexecdir@`.

Research notes:
- `CLEANFILES` removes the generated udev rule.
- `EXTRA_DIST` includes the rule template.
