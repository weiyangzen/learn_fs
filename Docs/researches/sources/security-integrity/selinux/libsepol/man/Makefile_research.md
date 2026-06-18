# sources/security-integrity/selinux/libsepol/man/Makefile

Purpose: Installs libsepol manual pages.

Important APIs and targets: Empty `all`; `install` creates man3/man8 destination directories, installs `man3/*.3` and `man8/*.8`, and loops over `LINGUAS` to install translated manpages when language-specific directories exist.

Control flow: The target uses shell conditionals inside a `for lang in $(LINGUAS)` loop to copy translated sections selectively.

State and persistence: Writes installed manpage files under `$(DESTDIR)$(MANDIR)` and language subdirectories.

Dependencies and integration points: Used by package/install workflows; variables include `PREFIX`, `MANDIR`, `MAN3SUBDIR`, `MAN8SUBDIR`, and `LINGUAS`.

Risks: Globs fail if no manpages exist depending on shell/install behavior. Translated directories are optional and silently skipped.

Test signals: `make install DESTDIR=... LINGUAS=...` and verifying expected man3/man8 files validates it.
