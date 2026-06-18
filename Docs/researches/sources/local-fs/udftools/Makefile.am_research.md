# File Research: sources/local-fs/udftools/Makefile.am

Top-level Automake orchestration.

Builds subdirectories in this order:
`libudffs`, `mkudffs`, `cdrwtool`, `pktsetup`, `udffsck`, `udfinfo`, `udflabel`, `wrudf`, and `doc`.

Installs documentation files through `dist_doc_DATA`: `AUTHORS`, `COPYING`, `NEWS`, and `README`.

Adds `autogen.sh` and `Doxyfile` to the distribution tarball through `EXTRA_DIST`.

No runtime behavior; this is root build/distribution glue.
