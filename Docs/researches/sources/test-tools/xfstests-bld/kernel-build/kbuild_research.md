# sources/test-tools/xfstests-bld/kernel-build/kbuild

Purpose: convenience kernel build driver for external object directories. It reads per-repository kbuild configuration, canonicalizes architecture, optionally installs configs, builds kernels or Debian packages, generates modules tarballs, and persists build config/cert material.

Important options: `--arch`, `--arm64`, `--i386`/`-32`, `--dpkg`, `--no-dpkg`, `--install-kconfig`, `--install-kconfig-opts`, `--oldconfig`, `--get-build-dir`, `--get-kbuild-config`, `--get-kbuild-dir`, `--no-action`, `--kunit`/`--test`, and `-j`.

Control flow: discovers git dir/common dir, ensures kernel source root, loads `.git/kbuild/config`, sets architecture/build dir overrides, builds `MAKE_ARGS` with `ARCH`, `O`, `CROSS_COMPILE`, and optional `CC=clang`, optionally runs install-kconfig/olddefconfig/KUnit, removes stale `.deb` symlinks, then either runs `make bindeb-pkg` and normalizes generated `.deb` names or runs ordinary `make`. On successful full builds it writes `.git_version`, installs modules into a temp dir, creates `modules.tar.xz`, and copies `.config` plus signing keys back to `.git/kbuild`.

State/persistence: creates/uses `$GITDIR/kbuild`, `$BLD_DIR`, `$BLD_DIR/.config`, `$BLD_DIR/modules.tar.xz`, normalized Debian package files, `.git_version`, and cached cert/key files.

Dependencies/integration: depends on git, Linux kernel make targets, dpkg tools for package mode, `arch-funcs`, install-kconfig, tar/xz, and optional clang/cross-compile settings. Outputs are consumed by kvm/gce xfstests.

Risks: build-directory selection depends on shell-sourced config. Debian version-number handling has kernel-version-specific logic. No-action mode still evaluates many shell tests. Module archive generation uses temp directories and must clean up on errors.

Test signals: `--get-build-dir`, no-action builds, package builds, successful `modules.tar.xz`, and subsequent kvm/gce boot tests validate this script.
