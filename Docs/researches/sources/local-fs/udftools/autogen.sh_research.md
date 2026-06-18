# File Research: sources/local-fs/udftools/autogen.sh

Short bootstrap script for regenerating autotools files.

Flow:
- Removes `autom4te.cache` and generated `libtool` trees.
- Runs `aclocal`.
- Runs `libtoolize --force --copy`.
- Runs `autoheader`.
- Runs `automake --add-missing --copy`.
- Runs `autoconf`.

No argument parsing or error handling beyond shell command exit behavior.
