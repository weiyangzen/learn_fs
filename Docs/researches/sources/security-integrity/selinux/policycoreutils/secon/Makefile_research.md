<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/secon/Makefile -->
# sources/security-integrity/selinux/policycoreutils/secon/Makefile

## Purpose
Builds and installs `secon`, a command-line SELinux context inspection utility.

## Important APIs, Types, And Functions
Defines strict warning flags in `WARNS`, reads `VERSION` from `../VERSION`, adds libselinux include/library paths, and uses `LIBSELINUX_LDLIBS`. Targets are `all`, `secon`, `install-nogui`, `install`, `relabel`, `clean`, and `bare`.

## Control Flow
`all` builds `secon` from `secon.o`. `install` copies the binary to `$(BINDIR)`, installs `secon.1`, and installs localized man1 files. `relabel` calls `/sbin/restorecon` on the installed binary. `bare` aliases cleanup.

## State And Persistence
The build creates `secon` and object files; install persists the binary and man pages.

## Dependencies And Integration Points
Depends on libselinux and the parent policycoreutils build exports. `secon` is also used by scripts such as `fixfiles` to extract context types.

## Risks And Edge Cases
The aggressive warning profile can expose portability issues across compilers. Install does not create `$(BINDIR)` before copying, so packaging must ensure it exists.

## Test Signals
Compile with the configured warning set, install into a staging root, run `secon --version`, and relabel the installed binary when SELinux is active.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/secon/Makefile -->
