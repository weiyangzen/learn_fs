# sources/security-integrity/audit-userspace/init.d/Makefile.am

Purpose: Automake rules for auditd system integration files: systemd units, default configs, tmpfiles config, augenrules script, bash completion, and optional legacy action scripts.

Important variables and targets: Installs `auditd.conf` and `audit-stop.rules` into `$(sysconfdir)/audit`, builds `auditd.service`, `audit-rules.service`, and `augenrules` from templates, installs units under `$(prefix)/lib/systemd/system`, installs `libaudit.conf` directly under `$(sysconfdir)`, and installs tmpfiles config as `$(prefix)/lib/tmpfiles.d/audit.conf`. Conditional `INSTALL_LEGACY_ACTIONS` installs rotate/resume/reload/state/stop/restart/condrestart scripts.

Control flow: Pattern rule substitutes `@runstatedir@`, `@sbindir@`, and `@sysconfdir@` into service templates. `install-data-hook` creates config/tmpfiles destinations. `install-exec-hook` creates unit and bash completion directories, installs generated units, chmods `augenrules`, and optionally installs legacy actions. `uninstall-hook` removes installed artifacts.

State and persistence: Persists system config files, generated systemd units, tmpfiles declaration, bash completion, and optional legacy scripts into target filesystem during install.

Dependencies and integration: Driven by `configure.ac` substitutions and automake conditionals. Integrates with systemd, tmpfiles.d, auditd config layout, and package install/uninstall steps.

Risks: Unit directory is fixed to `$(prefix)/lib/systemd/system`, which can differ by distro. `libaudit.conf` is installed with mode 640 and path `${sysconfdir}` because libaudit expects `/etc/libaudit.conf`. Uninstall removes files without `-f`, so partial installs may error. Packaging must preserve config semantics and not overwrite administrator changes carelessly.

Test signals: `make -C init.d install DESTDIR=...`, inspect generated substitutions, file modes, install paths, and `make uninstall` behavior. Confirm `INSTALL_LEGACY_ACTIONS` toggles legacy scripts.
