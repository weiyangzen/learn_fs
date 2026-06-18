# sources/user-network-fs/nfs-utils/Makefile.am

Purpose: this is the top-level Automake entry for nfs-utils. It defines subdirectories, distributed macro/bootstrap files, aclocal search paths, and install/uninstall hooks for NFS state directories.

Important variables and targets: `AUTOMAKE_OPTIONS = foreign`; `SUBDIRS = support tools utils linux-nfs tests systemd`; `EXTRA_DIST` includes `autogen.sh` and aclocal macros; `ACLOCAL_AMFLAGS = -I aclocal`. `install-data-hook` creates `$(statedir)` files (`etab`, `rmtab`) and statd state directories/files under `$(statdpath)`, permissions them, and attempts ownership by `$(statduser)`. `uninstall-hook` removes state files.

Control flow: Automake recurses into subdirectories during build/install. Hooks run during data install/uninstall after normal target actions.

State and persistence: installation creates persistent runtime state under configured NFS and statd state directories. These files are not build artifacts; they are daemon state placeholders.

Dependencies and integration points: integrates with variables substituted by `configure.ac` (`statedir`, `statdpath`, `statduser`) and the recursive Automake tree.

Risks: uninstall removes state files directly and may fail if missing; install uses `-chown` to ignore ownership failures. Package managers may prefer owning directories/files explicitly rather than hook-created state. `xtab` removal remains in uninstall even install creates `etab`/`rmtab`.

Test signals: run `make install DESTDIR=...` and inspect state paths, modes, and ownership behavior; run `make dist` to ensure `EXTRA_DIST` covers bootstrap macro files.
