# sources/security-integrity/selinux/libsemanage/man/Makefile

Purpose: installs libsemanage manual pages for section 3 API documentation and section 5 configuration files, including localized variants.

Important APIs/targets: variables include `PREFIX`, `MANDIR`, `MAN3SUBDIR`, `MAN5SUBDIR`, `MAN3DIR`, `MAN5DIR`, and `LINGUAS`. `install` creates target man directories, installs `man3/*.3` and `man5/*.5`, then repeats for each language with `lang/man3` or `lang/man5` subdirectories.

Control flow: package builds invoke `make install`; the target stages English man pages first and conditionally stages translated pages only when the relevant directories exist.

State and persistence behavior: writes documentation files under `$(DESTDIR)$(MANDIR)` and does not modify source files. `all` is intentionally empty.

Dependencies and integration points: used by top-level SELinux userspace installation. It must stay aligned with public headers and API behavior so generated packages ship matching docs.

Risks: glob install failures can occur if expected `man3` or `man5` files are absent. The loop assumes shell semantics and unquoted variables. Test signals include staged package inspection for all man sections and language-specific directory layouts.
