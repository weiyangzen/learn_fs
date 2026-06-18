# `sources/test-tools/fio/.github/workflows/ci.yml`

Purpose: Main fio CI workflow covering container builds, native Linux/macOS/Windows/Android-style builds, smoke tests, full tests, and Windows installer artifacts.

Important jobs and settings: Triggers are push, pull request, manual dispatch, and a daily scheduled run. `build-containers` runs distro container matrices for Debian, Fedora, Alma, Oracle, Rocky, and Ubuntu i686/x86_64. `build` runs a platform matrix for GCC, clang, macOS, Linux i686, Android target, Cygwin 32/64, and MSYS2 64, with install/build/smoke/full test scripts. Windows jobs install Cygwin or MSYS2 packages, build MSI installers, upload artifacts, and publish tagged Cygwin release assets.

Control flow: Each job checks out the repo, installs dependencies using `ci/actions-install.sh`, builds with `ci/actions-build.sh`, then runs smoke and full tests. Windows-specific steps handle line endings, toolchain installation, installer build, and dependency file cleanup.

State and persistence: Produces build outputs and optional Windows MSI artifacts. CI environment variables encode target build, architecture, OS, and compiler.

Dependencies and integration: Depends on GitHub Actions, container images, platform runners, Cygwin/MSYS2 third-party actions, fio CI scripts, and artifact/release actions.

Risks and test signals: Matrix includes an `android-recovery` include entry without a matching `build` list value, so it may not run unless GitHub matrix include semantics create it as intended. Action versions like `actions/checkout@v6` and upload-artifact v6 require current availability. Tests are the workflow itself; monitor dependency installation, installer creation, and full-test runtime across OSes.
