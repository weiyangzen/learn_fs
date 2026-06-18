<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/workflows/ci.yml -->
# sources/user-network-fs/s3fs-fuse/.github/workflows/ci.yml

Purpose: Defines the s3fs-fuse CI pipeline across Linux containers, macOS, memory/sanitizer lanes, and static analysis lanes.

Important jobs and controls: Triggered by push, pull request, and weekly Sunday cron. The Linux job runs a broad container matrix including Ubuntu, Debian, Rocky Linux, Fedora, openSUSE, and Alpine with privileged FUSE access. The macOS job uses fuse-t and Homebrew packages. MemoryTest covers glibc debug, address/undefined/thread sanitizers, thread-safety warnings, and Valgrind on Fedora. `static-checks` builds and runs clang-tidy, cppcheck, and shellcheck.

Control flow: Linux containers install pre-checkout prerequisites where needed, check out with `actions/checkout@v6`, run `.github/workflows/linux-ci-helper.sh` to install OS packages and export configure options, then run `./autogen.sh`, `./configure`, `make`, and test suites. Memory lanes set `CXX`, `CXXFLAGS`, sanitizer options, valgrind options, and S3 test URL via `$GITHUB_ENV` before build/test.

State and persistence: CI state is ephemeral container or runner state. The workflow relies on privileged runners with `/dev/fuse` and on `$GITHUB_ENV` to pass helper-derived variables across steps.

Dependencies and integration points: Integrates with autotools files (`autogen.sh`, `configure.ac`, Makefiles), test directories, the Linux helper script, FUSE kernel support, Homebrew fuse-t, and static analyzers. It is the main executable test signal for the s3fs subset.

Risks: Container tags reference future/current distro versions and may break as images or package names change. Privileged FUSE access may be constrained by hosted runner policy. `actions/checkout@v6` availability must align with GitHub Actions release state. Some sanitizer settings alter kernel sysctl values inside privileged containers.

Test signals: The workflow itself runs build, unit tests, integration tests, static analysis, sanitizers, and Valgrind. For edits to build scripts or cache/header code, passing Linux, macOS, static-checks, and relevant MemoryTest lanes is the strongest signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/workflows/ci.yml -->
