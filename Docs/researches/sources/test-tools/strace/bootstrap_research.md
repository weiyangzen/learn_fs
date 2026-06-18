<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bootstrap -->
# sources/test-tools/strace/bootstrap

Purpose: strace bootstrap script that regenerates generated build/test inputs and runs Autotools setup.

Important commands: runs generator scripts for BPF m4 attributes, mpers automake fragments, xlat tables, pure executable tests, SELinux context tests, and test lists. For `m32` and `mx32`, creates `tests-m32`/`tests-mx32`, transforms `tests/Makefile.am` placeholders and compiler flags with `sed`, symlinks most test files, and special-cases `*--secontext.c`. Copies `dist/README` and `dist/INSTALL`, then runs `autoreconf -f -i "$@"`.

Control flow: `sh -eu` aborts on unset variables or failed commands. Two compat test directories are regenerated in a loop.

State and persistence: rewrites generated test directories, copies docs, updates Autotools helper files.

Dependencies and integration: depends on numerous repo generator scripts, `sed`, `tr`, symlinks, and Autoconf/Automake/Libtool.

Risks: destructive `rm -rf tests-$m` is expected but broad if variables change. Sed substitutions must track `tests/Makefile.am` structure. Test signals: run `./bootstrap`, then `./configure`, and verify generated `tests-m32`/`tests-mx32` build files are valid.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bootstrap -->
