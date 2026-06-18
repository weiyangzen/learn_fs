# sources/user-network-fs/nfs-utils/autogen.sh

Purpose: `autogen.sh` cleans generated Autotools artifacts and regenerates the configure/build system for nfs-utils from source.

Important commands: it removes common helper files (`compile`, `config.guess`, `config.sub`, `depcomp`, `install-sh`, `ltmain.sh`, `missing`, `mkinstalldirs`), generated files (`aclocal.m4`, `configure`, `config.h.in`), `autom4te.cache`, all `Makefile.in`, and all `Makefile`. Unless invoked as `autogen.sh clean`, it runs `aclocal -I aclocal`, `libtoolize --force --copy`, `autoheader`, `automake --add-missing --copy --gnu`, and `autoconf`.

Control flow: cleanup always runs first. A literal first argument `clean` exits before regeneration.

State and persistence: it deletes and recreates generated build-system files in the source tree. This is intentionally destructive to generated artifacts but not to source files.

Dependencies and integration points: depends on Autotools, libtool, local `aclocal/` macros, and the Automake/Autoconf definitions in `configure.ac`/`Makefile.am`.

Risks: removing every `Makefile` below the tree can wipe local configured build directories if run in-tree. `echo -n` portability varies by shell. The script uses `set -e`, so missing tools abort the bootstrap.

Test signals: run `./autogen.sh clean` to verify cleanup-only mode, then run `./autogen.sh` in a clean checkout to confirm all generated files are recreated.
