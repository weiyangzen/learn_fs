# sources/test-tools/liburing/.github/workflows/ci.yml

## sources/test-tools/liburing/.github/workflows/ci.yml

Purpose: GitHub Actions CI pipeline for liburing. It validates many compiler/architecture combinations, sanitizer variants, installability, out-of-source builds, Alpine/musl compatibility, spelling, and shell scripts.

Important APIs/types/functions: GitHub Actions jobs `get_commit_list`, `build`, `out-of-source-build`, `alpine-musl-build`, `codespell`, and `shellcheck`; matrix fields for architecture, compiler packages, compiler commands, sanitizer settings, and extra flags. It invokes `./configure`, `make`, `sudo make install`, and compiles `.github/workflows/test_build.c` against installed `-luring`.

Control flow: first job computes a reverse commit list from push commits or falls back to current SHA. All other jobs matrix over that list. Main build job installs appropriate cross or clang toolchains, runs configure/build in normal, ASAN/UBSAN, or TSAN mode, tests installation, then compiles a tiny C and C++ consumer. Separate jobs cover out-of-source build cleanliness, Alpine chroot build/install, codespell, and shellcheck.

State and persistence: CI creates build artifacts, installs into runner system paths with `sudo make install`, and writes summaries via `$GITHUB_OUTPUT`/`$GITHUB_STEP_SUMMARY`. Out-of-source job checks that ignored/untracked source-tree leakage, except `build`, is absent.

Dependencies/integration: integrates with Ubuntu 24.04, apt cross compilers, apt.llvm.org clang 22 installer, `jirutka/setup-alpine`, codespell, shellcheck, repo `configure`, top-level Makefile, and installed pkg/linker paths.

Risks: matrix is broad and expensive; commit-list expression can be fragile on non-push events with missing `github.event.commits[0]`. Clang install script is network-sensitive. The Alpine build uses `CFLAGS="$FLAGS"` but `FLAGS` is only defined in the main build job env, so Alpine may not receive intended warnings. Out-of-source final compile path references `.github/workflows/test_build.c` from inside build, relying on generated proxy Makefiles or working directory assumptions.

Test signals: successful multi-arch compilation with `-Werror`, sanitizer builds, install smoke tests, clean out-of-source tree, codespell clean run, and shellcheck success.
