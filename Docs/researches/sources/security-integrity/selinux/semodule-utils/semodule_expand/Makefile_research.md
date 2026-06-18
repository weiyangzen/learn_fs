# sources/security-integrity/selinux/semodule-utils/semodule_expand/Makefile

Purpose: builds and installs the `semodule_expand` binary and its manpage.

Important flow: defaults set `PREFIX`, `BINDIR`, `MANDIR`, and optional `LINGUAS`; `CFLAGS` defaults to `-Werror -Wall -W`, and `LDLIBS` appends `-lsepol`. The `all` target builds `semodule_expand`; installation creates binary and manpage directories, installs the executable mode `755`, installs `semodule_expand.8`, and copies localized manpages when language directories exist. `clean` removes the binary and object files.

State and persistence: outputs are `semodule_expand`, object files, and installed files under `DESTDIR`. Dependencies are C compiler defaults, libsepol, install utilities, and localized manpage directories. Risks: `-Werror` can break builds on newer compilers, no explicit source dependency is listed beyond make's implicit rule, and `test` is absent in the subdir. Test signals should include clean rebuilds, DESTDIR install verification, and compiler warning checks.
