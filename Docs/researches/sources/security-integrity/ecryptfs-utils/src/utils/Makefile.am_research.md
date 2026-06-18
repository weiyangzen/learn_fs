<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/utils/Makefile.am

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/Makefile.am_research.md`. Source lines read for this pass: 72.

## Purpose
Automake build/install manifest for eCryptfs command-line utilities, setuid-root sbin helpers, shell scripts, optional TPM key generation, and the small internal test program.

## Important APIs, Types, And Functions
Defines `rootsbin_PROGRAMS`, `bin_PROGRAMS`, `bin_SCRIPTS`, `noinst_PROGRAMS`, source lists, CFLAGS, LDADD dependencies, `EXTRA_DIST`, and an `install-exec-hook` that links `umount.ecryptfs_private` to `mount.ecryptfs_private`.

## Control Flow
Automake consumes the declarations to compile helpers against `libecryptfs`, keyutils, libgcrypt, and optionally TSPI. Install phase places root sbin helpers and user scripts in the expected locations.

## State And Persistence Behavior
No runtime state, but it controls installed filesystem layout and therefore PAM/script integration paths.

## Dependencies And Integration Points
Integrates with the top-level autotools build, `src/libecryptfs/libecryptfs.la`, keyutils, libgcrypt, TSPI, and generated `config.h`.

## Risks And Edge Cases
Incorrect install destinations or missing LDADD entries break PAM/session paths. The hardlink/symlink relation between mount and unmount private helper is behaviorally significant because mode is selected by argv[0].

## Test Signals
`make`, `make install`, and `ENABLE_TESTS` exercise compilation of the listed binaries; packaging tests should verify installed modes and paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/Makefile.am -->
