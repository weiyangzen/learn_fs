# sources/test-tools/strace/ci/install-dependencies.sh

## Purpose
Installs CI build dependencies for strace across compiler, architecture, kernel-header, libc, stacktrace, and validation matrix variants. It prepares Ubuntu/Debian runners for the later build-and-test script.

## Important APIs, Types, and Functions
Read coverage: 150 lines and 2792 bytes. Important shell variables include `TARGET`, `CC`, `KHEADERS`, `KBRANCH`, `STACKTRACE`, `CHECK`, `j`, `sudo`, `common_packages`, `packages`, `KHEADERS_INC`, and `git_installed`. Helper functions are `retry_if_failed`, which retries a command up to 100 times with one-second sleeps, `apt_get_install`, which lazily runs `apt-get update` once before installing without recommends/suggests, and `clone_repo`, which ensures git/CA certificates, resolves relative GitHub-style repository names using the current remote origin, and shallow-clones an optional branch.

## Control Flow
The script starts with `sh -ex`, detects parallelism with `nproc`, and conditionally uses `sudo`. It selects package sets based on `TARGET`: cross armhf tooling for aarch64 compat, `gcc-multilib` for x86/x32/x86_64/s390x, or plain gcc otherwise. If `CC` names a GCC version, it enables the Ubuntu toolchain PPA and installs target-specific compiler packages; clang installs the selected clang package; other compilers use the default package set. If `KHEADERS` looks like an owner/repo path, it clones that kernel tree, installs headers into `/opt/kernel`, removes the clone, and records `/opt/kernel/include`; otherwise it uses `/usr/include`.

For `CC=musl-gcc`, it clones strace's musl fork, configures/builds/installs musl into `/opt/musl`, adjusts target flags for x32 or x86, removes the clone, and symlinks kernel header directories into musl's include directory. `STACKTRACE=libdw` or `libunwind` installs corresponding development packages plus libiberty. `CHECK=valgrind` installs valgrind. Finally, if `/dev/kvm` exists, it chmods it world-readable/writable for CI tests.

## State and Persistence Behavior
The script mutates the CI host by installing apt packages, possibly adding a PPA, cloning and deleting temporary repositories, installing kernel headers under `/opt/kernel`, installing musl under `/opt/musl`, creating symlinks into `/opt/musl/include`, and changing `/dev/kvm` permissions. State is intentionally outside the source tree except temporary `kernel` and `musl` directories that are removed.

## Dependencies and Integration Points
Depends on POSIX shell, apt, optional sudo, nproc, add-apt-repository, git, make, kernel `headers_install`, rsync for custom headers, and Ubuntu package naming. It integrates with the CI environment variables consumed by `ci/run-build-and-tests.sh`, with strace's cross/personality build matrix, with custom kernel header testing, stacktrace backends, valgrind runs, and KVM-dependent tests.

## Risks and Edge Cases
The retry loop masks transient apt/network failures but can delay real failures for about 100 seconds per command. Relative repository URL rewriting assumes the current git remote has a GitHub-like path. Adding the toolchain PPA is Ubuntu-specific. Musl setup symlinks kernel header directories and may conflict if paths already exist. `/dev/kvm` chmod is privileged and intentionally broad for CI. Cross packages are tailored to known matrix targets rather than arbitrary architectures.

## Test Signals
Run the script in CI containers for default gcc, versioned gcc, clang, musl-gcc, custom `KHEADERS`, stacktrace variants, and valgrind. Verify installed compiler commands, `/opt/kernel/include` content for custom headers, `/opt/musl` for musl builds, no leftover `kernel` or `musl` directories, retry behavior on transient apt failures, and successful handoff to `run-build-and-tests.sh`.
