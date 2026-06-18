# sources/test-tools/cthon04/general/Makefile

Purpose: makefile for the general Connectathon tests and fixtures, especially producing large1.c, large2.c, and large3.c copies from large.c.

Important APIs/types/functions: variables DESTDIR, FILES, LARGE_SRC; targets all, large1.c, large2.c, large3.c, clean, copy, and dist.

Control flow: all depends on the generated large source copies and ensures runtests is executable. Each largeN.c target removes the old copy and copies large.c. clean removes timing files, objects, stat, and generated large source copies. copy/dist refresh DESTDIR with the listed fixtures.

State and persistence behavior: creates generated source files in place and changes runtests mode. copy/dist mutate DESTDIR.

Dependencies and integration points: supports general/runtests and the large compile workload. It packages shell scripts, C fixtures, mkdummy/rmdummy, nroff input, and test makefiles.

Risks: DESTDIR defaults to /no/such/path to force explicit override; copy/dist run rm -f in DESTDIR and assume it is safe; generated copies can be mistaken for independent sources.

Test signals: after make all, large1.c-large3.c should exist and runtests should be executable.
