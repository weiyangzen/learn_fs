# sources/user-network-fs/sshfs/test/travis-build.sh

## Purpose

`travis-build.sh` is a legacy CI build-and-test driver for SSHFS. It performs multiple Meson/Ninja builds, runs the pytest test suite, runs the standard compiler builds under Valgrind, and runs sanitizer builds for undefined behavior and address sanitization. It is designed for Travis-style Linux CI with `sudo` available.

## Important APIs, Types, And Functions

- `set -e` makes the script fail fast on an unhandled command failure.
- `ASAN_OPTIONS="detect_leaks=0"` disables leak detection for now, acknowledging unresolved leaks or false positives.
- `LSAN_OPTIONS="suppressions=${PWD}/test/lsan_suppress.txt"` points LeakSanitizer at the repository's suppression file.
- `TEST_CMD="python3 -m pytest --maxfail=99 test/"` is the common test invocation.
- The first loop builds with `gcc` and `clang`, runs `meson -D werror=true`, compiles with `ninja`, then runs the tests with `TEST_WITH_VALGRIND=true`.
- The sanitizer loop sets `CC=clang`, builds once with `-D b_sanitize=undefined` and once with `-D b_sanitize=address`, runs the test command, and installs each build.

## Control Flow

The script exports sanitizer environment variables, then iterates over `gcc` and `clang`. Each compiler build happens in a subshell so `cd build-${CC}` does not affect the parent shell. There is a dormant branch for `gcc-6` that would add `-D b_lundef=false`, but the active compiler list only contains `gcc` and `clang`. After each standard build, pytest runs with `TEST_WITH_VALGRIND=true`, which `test/util.py` converts into a `valgrind -q --` prefix for the SSHFS process.

After the compiler loop, the script runs `(cd "build-${CC}"; sudo ninja install)`. At that point `CC` is still the last loop value, `clang`, so this installs the `build-clang` tree. It then sets `CC=clang` explicitly and loops over `undefined` and `address` sanitizers. Each sanitizer build gets its own `build-${san}` directory, configures Meson with `b_lundef=false` to work around a documented clang/Meson linker issue, builds, runs pytest normally, and installs with `sudo ninja install`.

## State And Persistence Behavior

The script creates or reuses `build-gcc`, `build-clang`, `build-undefined`, and `build-address` directories in the current working tree. It mutates the host by running `sudo ninja install` for the clang build and for each sanitizer build. Environment variables exported at the top apply to all child Meson, Ninja, and pytest commands. The script does not clean build directories, so reruns can fail if directories already exist or can reuse stale configuration if manually altered.

## Dependencies And Integration Points

- Requires Bash because it uses `#!/bin/bash` and `==` inside `[ ... ]`.
- Requires Meson, Ninja, Python 3, pytest, GCC, Clang, Valgrind, sanitizer-capable Clang runtimes, and sudo privileges.
- Integrates with `test/util.py` through `TEST_WITH_VALGRIND=true`; that environment variable changes `base_cmdline` for the mounted SSHFS process.
- Depends on the SSHFS test prerequisites installed by `travis-install.sh`, especially FUSE/libfuse and passwordless localhost SSH.
- The release packaging script references this file, so it is part of the repository's distributed test tooling even if Travis itself is no longer the active CI provider.

## Risks And Edge Cases

- `mkdir "build-${CC}"` and `mkdir "build-${san}"` fail on rerun if the directories already exist.
- The special `gcc-6` branch is unreachable with the current compiler list, suggesting stale CI compatibility code.
- The post-loop install relies on `CC` retaining `clang`; adding another compiler to the loop changes which standard build is installed.
- `sudo ninja install` mutates `/usr/local` or the configured prefix in CI, which can hide missing runtime path setup or affect later test phases.
- Leak detection is disabled globally, so memory leaks are not caught by the ASan lane.
- Valgrind execution across the full matrix is slow and can expose timing-sensitive test failures.

## Test Signals

- Standard `gcc` and `clang` builds passing with `-D werror=true` signal warning-clean compilation across both compilers.
- `TEST_WITH_VALGRIND=true` passing means the integration tests can run SSHFS under Valgrind without detected severe memory errors or Valgrind-induced behavior changes.
- UndefinedBehaviorSanitizer and AddressSanitizer lanes passing signal no sanitizer-detected UB or memory safety failures under the pytest workload.
- Successful `sudo ninja install` checks install rules after the build and test steps.
