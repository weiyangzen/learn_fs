<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/Makefile -->
# sources/security-integrity/selinux/libselinux/utils/Makefile

## Purpose
Builds and installs libselinux command-line utilities.

## Important APIs, Types, And Functions
Defines compiler warning flags, include/link flags, target selection, PCRE-linked utilities, and install/clean rules. `TARGETS` defaults to every `*.c` utility except Android host builds, which only build `sefcontext_compile`.

## Control Flow
Make expands targets from source filenames, appends libselinux and optional PCRE/FTS link libraries, and installs binaries under `$(PREFIX)/sbin`.

## State And Persistence Behavior
Build outputs are utility binaries and object files; install writes to `$(DESTDIR)$(SBINDIR)`.

## Dependencies And Integration Points
Depends on `../src/libselinux`, headers in `../include`, optional libsepol for `sefcontext_compile`, PCRE flags for label utilities, and platform-specific Darwin adjustments.

## Risks And Test Signals
Risks include `-Werror` portability, Android target narrowing, static library linkage for `sefcontext_compile`, and missing PCRE flags. Test signals are full `make all`, Android-host build, Darwin build, install path staging, and clean/distclean.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/Makefile -->
