## sources/test-tools/fio/ci/actions-build.sh

Purpose: GitHub Actions build entrypoint for fio. It normalizes CI target OS/architecture, selects target-specific configure flags, runs `./configure`, and builds with parallel `make`.

Important flow: `main()` sources `ci/common.sh`, sets `extra_cflags="-Werror"`, calls `set_ci_target_os`, and switches on `CI_TARGET_BUILD/CI_TARGET_OS`. Android configures the NDK toolchain and `UNAME=Android`; Linux/Ubuntu x86_64 enables CUDA, libiscsi, and libnbd; i686 Linux-style builds add `-m32`; Windows disables native tuning, optionally selects 32-bit Windows, and disables TLS for MSYS2 64-bit. It appends `--extra-cflags` and uses `nproc` or macOS `sysctl` for job count.

State and persistence: it mutates environment variables such as `UNAME`, `PATH`, `LIBS`, `LDFLAGS`, and local configure arguments. It produces fio build outputs through `configure` and `make`.

Dependencies and integration: depends on CI-provided `CI_TARGET_BUILD`, `CI_TARGET_ARCH`, `CI_TARGET_OS`, the Android NDK installed by `actions-install.sh`, and tools installed by platform package steps.

Risks and test signals: `set -eu` catches unset variables except branches that intentionally test empty values. Build matrix changes can break case matching. Test signal is the full configure output and `make` result in CI; platform-specific flags should be checked against install script package coverage.
