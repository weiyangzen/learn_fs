# sources/security-integrity/selinux/semodule-utils/semodule_link/Makefile

Purpose: builds and installs the `semodule_link` utility and its manpage.

Important flow: it mirrors the other semodule utility makefiles: install directories default under `/usr`, `CFLAGS` enables warnings as errors, and `LDLIBS` links `-lsepol`. `all` builds `semodule_link` through implicit compilation; `install` installs the binary and `semodule_link.8`, including localized manpages from `LINGUAS`; `clean` removes artifacts.

State and persistence: local outputs are `semodule_link` and object files, while install writes to `$(DESTDIR)$(BINDIR)` and `$(DESTDIR)$(MANDIR)/man8`. Dependencies are libsepol and make/install tooling. Risks: no explicit dependency list beyond implicit make rules, no test target, and warning-as-error sensitivity to compiler updates. Test signals are clean build, DESTDIR install, localized manpage copy behavior, and link-time verification against libsepol.
