<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/Makefile.am

## Purpose

Top-level autotools packaging file for ksmbd-tools. It wires the addshare, adduser, control, mountd, and tools subdirectories into one distribution and install graph.

## Important APIs, Types, and Functions

Exports `SUBDIRS`, `EXTRA_DIST`, `pkgsysconfdir`, `dist_pkgsysconf_DATA`, `man_MANS`, and `systemdsystemunit_DATA`. It uses the configured `in_script` sed command to generate man pages and the systemd unit from `.in` templates.

## Control Flow

Autotools descends into subdirectories, distributes common include and build metadata, renders `ksmbd.conf.5`, `ksmbdpwd.db.5`, and `ksmbd.service`, then runs install hooks that create runtime/config directories and install a default config if absent.

## State and Persistence Behavior

Install-time state includes `$(runstatedir)`, `$(sysconfdir)/ksmbd`, the default `ksmbd.conf`, and installed generated man/unit files. The uninstall hook removes the installed config to keep distcheck clean.

## Dependencies and Integration Points

Depends on configure.ac substitutions, `ksmbd.conf.example`, template inputs, and all subdirectory Makefile.am files.

## Risks and Edge Cases

The install hook conditionally writes a default config, so packaging scripts must account for conffile ownership. The uninstall hook is distcheck-friendly but can surprise package managers if used outside a packaging context.

## Test Signals

`make distcheck`, install/uninstall into DESTDIR, and verification that generated templates contain correct sbindir, sysconfdir, runstatedir, and version substitutions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/Makefile.am -->
