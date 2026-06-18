<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/Makefile -->
# sources/security-integrity/libcap/Makefile

## Purpose
Top-level libcap makefile. It coordinates building, testing, cleaning, distribution checks, Go module version updates, and release tagging across libcap subprojects.

## Important APIs, Types, And Functions
Targets include `all`, `test`, `sudotest`, `install`, `clean`, `gomods-update`, `distclean`, `release`, `ktest`, `distcheck`, `morgangodoc`, and `morganrelease`. It includes `Make.Rules` and dispatches into `libcap`, `pam_cap`, `go`, `tests`, `progs`, `doc`, and `kdebug`.

## Control Flow
Pattern targets run local no-op `%-here` hooks, then recurse into subdirectories with feature gates for PAM and Go. `distclean` validates Go module versions, exported header versions, and a clean git tree. Release targets create tarballs and signed tags.

## State And Persistence Behavior
Build targets create binaries, libraries, docs, Go sums, tags, and tarballs depending on target. Clean/distclean remove generated artifacts and require repository cleanliness.

## Dependencies And Integration Points
Depends on make, git, gpg, Go, C toolchains, optional PAM, musl, clang, and recursive makefiles throughout libcap.

## Risks And Edge Cases
Release targets are destructive in the sense of creating signed tags and tarballs. `distclean` fails on any ignored or untracked state. Recursive subproject behavior depends on `Make.Rules` feature variables.

## Test Signals
Signals include successful recursive builds/tests, version consistency checks, and `distcheck` matrix coverage across dynamic/static, compiler, PAM, and musl configurations.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/Makefile -->
