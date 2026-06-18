## sources/test-tools/fio/ci/actions-install.sh

Purpose: installs platform-specific fio build and test dependencies in GitHub Actions environments.

Important APIs and flow: `_sudo()` runs commands with sudo when available. `install_ubuntu()` optimizes dpkg behavior, selects base packages, handles i686 multiarch, adds x86_64 engines and CUDA dependencies, and adds container/QEMU-specific packages. `install_fedora()` and RHEL clone helpers install DNF packages and enable required repositories for Oracle, Alma, and Rocky. `install_macos()` uses Homebrew and pip; `install_windows()` installs Python packages; Android downloads and unzips NDK r24. `main()` derives `CI_TARGET_OS` with `set_ci_target_os`, dispatches to `install_${CI_TARGET_OS}`, and prints Python path/version.

State and persistence: mutates host package databases, may add dpkg architecture/repository state, installs Python packages, and downloads Android NDK into the fio tree.

Dependencies and integration: sourced `common.sh` supplies target detection. Build and test scripts assume this script has installed compilers, libraries, headers, docs tools, and Python dependencies.

Risks and test signals: package names and repositories are distribution-version sensitive. `EXTRA_PKGS` is expanded into arrays and can affect shell word handling. Network/package mirror failures are common external risks. Successful subsequent `actions-build.sh`, smoke, and full-test lanes are the validation signal.
