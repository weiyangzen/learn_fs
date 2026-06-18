# sources/security-integrity/ecryptfs-utils/src/daemon/Makefile.am

Purpose: builds the `ecryptfsd` userspace daemon.

Important APIs/targets: `bin_PROGRAMS=ecryptfsd`; source `main.c`; CFLAGS include libgcrypt/keyutils flags; LDADD links `libecryptfs.la`, keyutils, and libgcrypt.

Control flow/state: Automake compiles and links the daemon into the installable binary set.

Dependencies/integration: depends on built libecryptfs and kernel key/messaging libraries.

Risks: daemon link flags must match configure substitutions; missing libgcrypt variable detection would break builds.

Test signals: daemon compile/link and any runtime daemon tests.
