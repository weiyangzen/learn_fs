<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/Makefile.am -->
# sources/user-network-fs/cifs-utils/Makefile.am

## Purpose

`Makefile.am` is the top-level Automake recipe for cifs-utils. It wires the always-built `mount.cifs` helper and conditional utilities such as `cifs.upcall`, `cifscreds`, `cifs.idmap`, `getcifsacl`, `setcifsacl`, `idmapwb.so`, `pam_cifscreds.so`, Python scripts, and generated man pages.

## Important APIs, Types, and Functions

The important variables are `AM_CFLAGS`, `root_exec_sbindir`, `root_exec_sbin_PROGRAMS`, `mount_cifs_SOURCES`, `resolve_hosts_SOURCES`, `resolve_hosts_LDADD`, `rst_man_pages`, `CLEANFILES`, and the conditional program/source/link groups guarded by `CONFIG_CIFSUPCALL`, `CONFIG_CIFSCREDS`, `CONFIG_CIFSIDMAP`, `CONFIG_CIFSACL`, `CONFIG_SMBINFO`, `CONFIG_PYTHON_TOOLS`, `CONFIG_PLUGIN`, `CONFIG_PAM`, and `CONFIG_MAN`.

## Control Flow

Automake expands the conditionals from `configure.ac`. `mount.cifs` is always built from `mount.cifs.c`, `mtab.c`, DNS/CLDAP resolver sources, and `util.c`; optional programs append to `bin_PROGRAMS`, `sbin_PROGRAMS`, `bin_SCRIPTS`, `plugin_PROGRAMS`, or `pam_PROGRAMS`. RST inputs are converted to `.1` or `.8` man pages through the `RST2MAN` suffix rules. Template rules substitute `@sbindir@` and `@pluginpath@` into generated RST files.

## State and Persistence Behavior

The file persists build outputs, generated manpage intermediates, generated request-key snippets, install-time symlinks, and cleanup lists. Runtime persistence is outside the Makefile, but install hooks create `mount.smb3` and manpage symlinks to the CIFS helper.

## Dependencies and Integration Points

It integrates with Autoconf substitutions from `configure.ac`, libtalloc/libresolv for resolver sources, keyutils for keyring helpers, Kerberos/GSSAPI for `cifs.upcall`, `dl` for idmap plugin loading, wbclient for `idmapwb.so`, PAM for `pam_cifscreds.so`, and docutils `rst2man` for manpage generation.

## Risks and Edge Cases

Conditional build drift can silently omit a utility or manpage when a dependency check changes. The plugin and PAM shared objects are hand-linked with `-shared -fpic`, so flags and library ordering matter. Generated RST files must stay listed in `CLEANFILES` or stale substituted paths can survive rebuilds. The uninstall hook references destination paths directly and must keep `DESTDIR` handling correct.

## Test Signals

Useful signals are `autoreconf && ./configure` with all optional features enabled and disabled, `make distcheck`, install/uninstall dry runs with `DESTDIR`, generated manpage diffs, and package builds that confirm every conditional utility links with the expected libraries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/Makefile.am -->
