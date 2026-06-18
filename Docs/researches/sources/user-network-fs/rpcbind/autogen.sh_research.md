# sources/user-network-fs/rpcbind/autogen.sh

## Purpose
Cleans generated autotools files and regenerates the build system.

## APIs, Flow, And State
The shell script removes common generated helper files, `aclocal.m4`, `configure`, `config.h.in`, `autom4te.cache`, `Makefile.in`, and `Makefile`. With argument `clean`, it exits after cleanup. Otherwise it runs `aclocal`, `automake --add-missing --copy --gnu`, and `autoconf`.

## Dependencies And Integration
Requires POSIX shell utilities plus autotools. It is used by developers/packagers before running configure from a source checkout.

## Risks And Test Signals
It destructively removes generated build files in the tree. There is no quoting issue for the fixed filenames, and `find -print0 | xargs -r0` handles paths safely. Test signal is successful regeneration and subsequent configure/make.
