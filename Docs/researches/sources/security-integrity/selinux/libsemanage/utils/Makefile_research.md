# sources/security-integrity/selinux/libsemanage/utils/Makefile

## Purpose
This Makefile installs libsemanage utility scripts, currently the `semanage_migrate_store` Python tool, into the SELinux libexec directory.

## Important Targets and Variables
`PREFIX` defaults to `/usr`, `LIBEXECDIR` defaults to `$(PREFIX)/libexec`, and `SELINUXEXECDIR` defaults to `$(LIBEXECDIR)/selinux/`. Targets are `all`, `install`, `clean`, `distclean`, and `relabel`. Only `install` performs work: it creates `$(DESTDIR)$(SELINUXEXECDIR)` and installs `semanage_migrate_store` mode `755`.

## Control Flow
`all`, `clean`, and `relabel` are empty. `distclean` delegates to `clean`. `install` runs after `all`, creates the destination directory with a leading dash to ignore errors, then copies the script with executable permissions.

## State and Persistence Behavior
The Makefile writes only to the installation tree selected by `DESTDIR`, `PREFIX`, and related variables. It does not build generated artifacts.

## Dependencies and Integration Points
It is invoked by the parent libsemanage build. Runtime behavior of the installed utility depends on Python and SELinux bindings, but this Makefile only requires standard `make`, `mkdir`, and `install`.

## Risks and Test Signals
The ignored `mkdir` failure can hide installation-directory problems until the `install` command fails. There is no uninstall target. The test signal is a successful `make -C utils install DESTDIR=...` producing an executable `libexec/selinux/semanage_migrate_store`.
