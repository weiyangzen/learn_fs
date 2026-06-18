# sources/user-network-fs/samba/source3/script/wscript_build

Purpose: Waf build/install declarations for selected Samba source3 scripts.

Important functions and APIs: imports `MODE_755`, calls `bld.INSTALL_FILES()` for `smbtar` and `samba-log-parser` into `${BINDIR}`, conditionally installs `winbind_ctdb_updatekeytab.sh` into `CTDB_DATADIR/scripts`, and declares `bld.SAMBA_SCRIPT()` wrappers for `smbaddshare`, `smbchangeshare`, and `smbdeleteshare`.

Control flow: all statements run at build-description evaluation time; only the CTDB script install is conditional on `conf.env.with_ctdb`.

State and persistence: affects the build/install manifest rather than runtime state. It determines which scripts are installed and with executable mode.

Dependencies and integration: part of Samba's Waf build system. It depends on `samba_utils.MODE_755`, `bld`, `conf`, and environment variables such as `CTDB_DATADIR`.

Risks and test signals: install path mistakes affect packaging/runtime availability of helper scripts, especially the CTDB keytab update hook. Build/install tests or packaging manifests are the primary signals.
