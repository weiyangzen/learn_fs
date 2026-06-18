# sources/sync-backup/rsync/prepare-source.mak

Purpose: Minimal makefile for regenerating rsync autoconf artifacts used by `prepare-source`.

Important APIs, types, and functions: Targets are `conf`, `aclocal.m4`, `configure.sh`, and `config.h.in`. Commands call `aclocal -I m4`, `autoconf -o configure.sh`, and `autoheader && touch config.h.in`.

Control flow: `conf` depends on `configure.sh` and `config.h.in`. `aclocal.m4` is regenerated from `m4/*.m4`; both generated outputs depend on `configure.ac` and `aclocal.m4`.

State and persistence behavior: Writes generated autoconf files in the current directory. Uses standard make timestamp logic and does not store custom state.

Dependencies and integration points: Invoked by `prepare-source`; requires `make`, `aclocal`, `autoconf`, `autoheader`, `configure.ac`, and `m4` macros.

Risks and test signals: Risks are mostly tool-version drift and generated-file churn. Test by invoking `make -f prepare-source.mak conf` in a prepared tree and comparing generated files expected by build scripts.
