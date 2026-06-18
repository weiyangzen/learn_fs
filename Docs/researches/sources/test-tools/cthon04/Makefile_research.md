# sources/test-tools/cthon04/Makefile

Purpose: top-level Makefile for the Connectathon 2004 testsuite. It builds helper programs and recursively builds/copies/distributes basic, general, special, tools, and lock test subdirectories.

Important APIs/types/functions: variables `DESTDIR`, `COPYFILES`, `include tests.init`, targets `all`, `lint`, `domount`, `getopt`, `clean`, `copy`, `dist`, `tar`, `rpm`, and `mknewdirs`. `domount` is built from `domount.c` and made setuid root.

Control flow: `all` builds `domount` and `getopt`, runs make in each subdirectory, and ensures `runtests` is executable. `copy` and `dist` create destination subdirectories and copy binaries or sources recursively. `tar` packages a distribution tree; `rpm` runs `rpmbuild`.

State/persistence behavior: creates binaries, changes ownership/mode of `domount`, copies files into `DESTDIR`, creates tarballs, and may invoke RPM build tooling. Dependencies/integration: expects `tests.init`, subdirectory makefiles, C compiler variables, and root permissions for chown/setuid.

Risks/test signals: default `DESTDIR` is invalid to prevent accidental copy, `-chown` ignores failure, recursive makes propagate environment assumptions, and setuid root helper creation is security-sensitive.
