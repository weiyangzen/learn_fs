## sources/security-integrity/libcap/doc/Makefile

Purpose: builds, installs, and optionally renders libcap/libpsx manual pages.

Important targets/variables: `MAN1S`, `MAN3S`, `MAN5S`, `MAN7S`, `MAN8S`, aggregate `MANS`, `all`, `html`, `install`, `clean`, `test`, and `sudotest`.

Control flow: includes `Make.Rules`, treats all listed manpage files as the default build product, renders HTML with `groff -man -Thtml` while skipping `.so man` redirect pages, installs manpages into section-specific `$(MANDIR)/manN` directories using a destination-state loop, and removes generated `html` output on clean.

State/persistence: creates `html/` and installs manpages under `$(FAKEROOT)$(MANDIR)`.

Dependencies/integration: GNU make, project `Make.Rules`, `groff`, install utilities, and the manpage source files. Integrated with top-level libcap build/install flows.

Risks: install loop is compact and depends on absolute-path markers to switch section destinations; missing manpage entries silently break packaging completeness. HTML generation skips redirect pages and may leave crosslinks unresolved.

Test signals: `make -C doc all`, `make -C doc html`, staged `make install FAKEROOT=...`, and package checks confirming every public API in `sys/capability.h` has a corresponding manpage.
