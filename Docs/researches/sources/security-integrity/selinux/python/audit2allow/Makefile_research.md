<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/Makefile -->
# sources/security-integrity/selinux/python/audit2allow/Makefile

## Purpose
Builds, tests, and installs `audit2allow`, the `audit2why` symlink, `sepolgen-ifgen`, and the C attribute helper.

## Important APIs, Types, And Functions
Defines `PYTHON`, `SECILC`, install directories, CFLAGS/LDFLAGS for libselinux, optional `LIBSEPOLA`, `LDLIBS_LIBSEPOLA`, and targets `audit2why`, `sepolgen-ifgen-attr-helper`, `test_dummy_policy`, `test`, `install`, `clean`, and `relabel`.

## Control Flow
`all` creates the `audit2why` symlink and builds the helper. The helper links against static or fallback libsepol and libselinux. `test` builds a dummy binary policy from CIL using `secilc`, then runs `test_audit2allow.py`. `install` copies scripts and helper to bindir, recreates the `audit2why` symlink, and installs man pages and localized man pages.

## State And Persistence
Build outputs include the helper binary, object files, `audit2why` symlink, and `test_dummy_policy`. Install persists command-line tools and man pages.

## Dependencies And Integration Points
Depends on Python sepolgen modules, libselinux, libsepol, `secilc`, and test fixtures in the directory.

## Risks And Edge Cases
Static libsepol selection can vary by build environment. `audit2why` behavior is name-sensitive because the Python source checks basename. Tests require local execution from the source directory.

## Test Signals
`make test`, helper link success, symlink correctness, script install permissions, and successful `audit2allow`/`audit2why` execution against `test_dummy_policy`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/Makefile -->
