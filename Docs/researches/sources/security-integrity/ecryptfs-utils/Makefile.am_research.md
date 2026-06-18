# sources/security-integrity/ecryptfs-utils/Makefile.am

Purpose: top-level Automake file for ecryptfs-utils distribution and recursive builds.

Important APIs/targets: sets foreign Automake mode with bzip2 dist, `ACLOCAL_AMFLAGS=-I m4`, extensive `MAINTAINERCLEANFILES`, `SUBDIRS = doc src po tests`, `EXTRA_DIST = autogen.sh`, installs `README`, and ensures `m4` exists in `dist-hook`.

Control flow/state: drives recursive build and distribution packaging.

Dependencies/integration: consumed by Autotools generated Makefiles and aligned with `configure.ac` subdir configuration.

Risks: `MAINTAINERCLEANFILES` includes generated Autotools files and Debian directory, so maintainer-clean can remove packaging scaffolding. Recursive `SUBDIRS` assumes all configured directories exist.

Test signals: `make dist`, maintainer-clean, and recursive build success validate it.
