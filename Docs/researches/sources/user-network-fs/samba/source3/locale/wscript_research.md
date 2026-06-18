# sources/user-network-fs/samba/source3/locale/wscript

Purpose: `source3/locale/wscript` wires Samba locale catalogs into the waf build.

Important API: `build(bld)` imports `Options` and checks both `not Options.options.disable_gettext` and presence of `MSGFMT` in `bld.env`. If enabled, it registers two `intltool_po` build features: appname `net` with `podir='net'`, and appname `pam_winbind` with `podir='pam_winbind'`, both installed under `${LOCALEDIR}`.

Control flow and state: build registration is conditional. If gettext is disabled or `msgfmt` was not found, no locale build tasks are registered. No runtime state is created by this script itself; generated/installed `.mo` files are build artifacts.

Dependencies and integration: depends on waflib `Options`, waf gettext/intltool support, `MSGFMT` detection, locale directories, and Samba's `LOCALEDIR` install variable. It integrates with the `genmsg` scripts that refresh source `.po` files.

Risks: missing `MSGFMT` silently prevents catalog builds under this condition, which may surprise package builders expecting translations. Adding a new catalog requires updating this script. Incorrect `appname` or `podir` breaks install paths or domain names.

Test signals: configure/build with gettext enabled and `msgfmt` present should register and install `net` and `pam_winbind` catalogs. Builds with `--disable-gettext` or no `MSGFMT` should skip them cleanly.
