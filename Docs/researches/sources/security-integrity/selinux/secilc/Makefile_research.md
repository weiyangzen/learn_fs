# sources/security-integrity/selinux/secilc/Makefile
# sources/security-integrity/selinux/secilc/Makefile

Purpose: builds, tests, installs, documents, and cleans `secilc` CIL compiler utilities.

Important APIs and control flow: defines targets for `secilc`, `secil2conf`, `secil2tree`, and `secilcheck`, links with `-lsepol`, generates manpages from XML with `xmlto`, runs tests by compiling sample CIL and comparing optimized output through `checkpolicy`, installs binaries/manpages, delegates docs to `docs/`, and cleans binaries, objects, generated policy files, manpages, and test outputs.

State and persistence: build outputs, generated manpages, test output files, and installed binaries/manpages.

Dependencies and integration points: depends on libsepol, checkpolicy, xmlto, compiler, and docs Makefile. Integrated into top-level SELinux build/release.

Risks and test signals: `POL_VERS` depends on installed `checkpolicy -V`; mismatches can affect tests. Test target provides concrete regression signal for CIL compilation and optimizer output.
