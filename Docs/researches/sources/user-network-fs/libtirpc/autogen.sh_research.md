<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/autogen.sh -->
# sources/user-network-fs/libtirpc/autogen.sh

Purpose: Bootstrap script for regenerating libtirpc Autotools files from a clean source checkout.

Important APIs, types, and functions: Removes generated files/directories, supports `clean` mode, then runs `aclocal`, `libtoolize --force --copy`, `autoheader`, `automake --add-missing --copy --gnu`, and `autoconf`.

Control flow: First deletes known generated files plus all `Makefile.in` and `Makefile`, then exits if requested or recreates the build system.

State and persistence behavior: Mutates the source tree by removing and regenerating build files.

Dependencies and integration points: Depends on Autotools/libtool. Used by developers and packaging workflows.

Risks: Deletes all `Makefile` files under the tree, which is expected for bootstrap but destructive if local generated build state matters. `set -e` stops on first tool failure.

Test signals: Successful bootstrap and subsequent configure/build are the signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/autogen.sh -->
