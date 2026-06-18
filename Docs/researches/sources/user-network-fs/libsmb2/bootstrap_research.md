# sources/user-network-fs/libsmb2/bootstrap

Purpose: This tiny bootstrap script regenerates autotools infrastructure for libsmb2.

Important APIs and types: It is a POSIX shell script with a single command, `autoreconf -vif`.

Control flow: Running the script invokes autoreconf in verbose, install, and force modes so local `configure`, aclocal files, libtool helper files, and Automake support files are regenerated from `configure.ac` and `Makefile.am` inputs.

State and persistence behavior: The script writes generated autotools files into the source tree. It does not track state itself.

Dependencies and integration points: It requires Autoconf, Automake, libtoolize/aclocal support, and the macros referenced by `configure.ac`, including local `m4` macros.

Risks: `autoreconf -i -f` can overwrite generated files and can produce different output depending on installed autotools versions. It should be run intentionally, not as an opaque build step in a dirty tree.

Test signals: Success is a zero exit status and a usable `./configure` script. Follow-up validation is `./configure && make`.
