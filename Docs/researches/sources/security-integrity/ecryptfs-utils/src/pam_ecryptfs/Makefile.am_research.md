# sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/Makefile.am

## Purpose
Automake definition for building and installing the `pam_ecryptfs` PAM module when PAM support is enabled. It links the module against the in-tree libecryptfs and PAM libraries.

## Important APIs, types, and functions
- `if BUILD_PAM` gates `pam_LTLIBRARIES = pam_ecryptfs.la`.
- `install-data-hook` removes installed `.la` and `.a` libtool archive artifacts from the PAM module directory.
- `uninstall-local` removes `pam_ecryptfs.so`.
- `pam_ecryptfs_la_SOURCES = pam_ecryptfs.c` identifies the module implementation.
- `pam_ecryptfs_la_LIBADD` links `src/libecryptfs/libecryptfs.la` and `$(PAM_LIBS)`.
- `pam_ecryptfs_la_LDFLAGS` builds a shared, module-style, avoid-version library.

## Control flow
No runtime control flow. Build flow is conditional on configure's `BUILD_PAM`; installation uses a hook to leave only the PAM shared object where PAM expects loadable modules.

## State and persistence behavior
Controls installed PAM module artifacts under `$(pamdir)`. It does not manage user keyrings or encrypted home state directly; that happens in `pam_ecryptfs.c` and libecryptfs at runtime.

## Dependencies and integration points
Bridges the PAM module with libecryptfs key-management and mount helper functionality. Depends on configure-provided `pamdir`, `PAM_LIBS`, and the built libecryptfs target.

## Risks and edge cases
Incorrect `pamdir` or disabled `BUILD_PAM` means no PAM integration is installed. The install hook assumes libtool archive names and removes them with `rm -f`; packaging scripts should still verify final artifacts. Because it links the in-tree libecryptfs, ABI or symbol changes in the library directly affect PAM authentication/session behavior.

## Test signals
Build tests should configure with and without PAM support, confirm `pam_ecryptfs.so` is produced only when expected, and verify `.la`/`.a` artifacts are removed from the staged PAM directory. Runtime tests belong to the PAM module implementation and should exercise login/session key insertion and unmount flows.
