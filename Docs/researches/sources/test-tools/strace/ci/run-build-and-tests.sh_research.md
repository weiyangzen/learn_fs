# sources/test-tools/strace/ci/run-build-and-tests.sh

## Purpose
Runs the strace CI build, configure, and test workflow after dependencies are installed. It applies matrix-specific compiler flags, stacktrace/check options, custom kernel headers, diagnostics, bootstrap/configure, normal or coverage/valgrind/distcheck test modes, and a final source-tree cleanliness check.

## Important APIs, Types, and Functions
Read coverage: 120 lines and 2935 bytes. Key variables include `DISTCHECK_CONFIGURE_FLAGS`, `CC`, `TARGET`, `STACKTRACE`, `KHEADERS`, `CHECK`, `CPPFLAGS`, `VERBOSE`, `VALGRIND_TOOLS`, `VALGRIND_TESTDIR`, `CC_FOR_BUILD`, `nproc`, `j`, and `j2`. It sets configure cache variables such as `st_cv_mx32_runtime=no` for clang x32 and coverage-tool cache variables for lcov/genhtml. Major commands are `git-set-file-times`, `bootstrap`, `configure`, `make all`, `make check`, `make check-valgrind-*`, `make distcheck`, log tailing, and `git status --porcelain`.

## Control Flow
The script exports default distcheck flags `--disable-dependency-tracking --enable-gcc-Werror`, adjusts clang x32 runtime detection, appends `-mx32` or `-m32` target flags, and adds configure options for stacktrace enable/disable. Custom kernel headers set `CPPFLAGS=-isystem /opt/kernel/include`. Coverage mode enables code coverage and supplies lcov/genhtml cache hits; valgrind mode enables valgrind. It prints environment diagnostics including uname, libc, shell file type, compiler version, multilibs, make/autoconf/automake versions, and kernel header version computed by preprocessing `<linux/version.h>`.

It exports `CC_FOR_BUILD`, normalizes file times, bootstraps autotools, and runs `./configure --enable-maintainer-mode` with the accumulated flags. On configure failure it dumps `config.log` and compiler specs before exiting. Coverage builds all with debug/`-Og`, runs checks, and tails test logs. Valgrind builds, runs selected valgrind test targets, tails logs, and preserves failure status. Default mode runs `make distcheck`. The final guard fails if git status shows source-tree changes.

## State and Persistence Behavior
Build outputs, generated autotools files, configured Makefiles, test logs, coverage files, valgrind logs, and distribution tarball artifacts are created in the working tree as part of the build. The final cleanliness guard requires the build system and tests to clean up after themselves for successful CI. Environment-variable exports persist only within the script process and child commands.

## Dependencies and Integration Points
Depends on POSIX shell, compiler toolchains, make, autoconf/automake, ldd, file, git, bootstrap prerequisites, optional lcov/genhtml, optional valgrind, optional custom kernel headers, and strace's generated autotools build. It integrates with `install-dependencies.sh`, `configure.ac` options, test-suite log files, ksysent generation logs, maintainer mode, mpers/cross targets, and CI failure diagnostics.

## Risks and Edge Cases
`ldd /bin/sh` parsing may fail for static or unusual shells, but the script mainly uses it for diagnostics. Kernel header version preprocessing assumes `LINUX_VERSION_CODE` is available. `make -k` preserves more failures but requires careful rc handling; valgrind mode captures failures across tools. The final git-clean check can fail if generated files or tests leave nondeterministic artifacts. x32 clang is forced off through a cache variable because the runtime probe is known to fail.

## Test Signals
Exercise default distcheck, coverage, valgrind, x86 `-m32`, x32, clang, stacktrace libdw/libunwind/no, and custom kernel-header modes. Confirm configure failure diagnostics include `config.log` and dumpspecs, test-suite logs are tailed on failures, coverage and valgrind flags reach configure, final git cleanliness catches generated drift, and output contains the expected environment information block.
