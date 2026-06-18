# sources/storage-engines/tikv/ci-build/Makefile

## Purpose
`ci-build/Makefile` defines legacy CI preparation, test, and coverage targets for Linux/macOS environments.

## Important APIs, types, and functions
It defines `CI_BUILD_DIR` and targets for building `gflags`, building/installing `kcov`, preparing Linux/macOS dependencies, running tests, and collecting coverage. Targets use `LOCAL_DIR`, `TRAVIS_OS_NAME`, and `TRAVIS_JOB_ID`.

## Control flow
Dependency targets download archives into `/tmp`, build with CMake/make or Xcode on macOS, and install into `LOCAL_DIR`. `test_linux`/`test_osx` set `CI=true` and call `ci-build/test.sh`. Coverage targets parse `tests.out` for test binaries and run `kcov` with include/exclude/strip settings.

## State and persistence behavior
It writes downloaded/build artifacts under `/tmp`, installs into `LOCAL_DIR`, writes coverage data under `target/kcov`, and relies on `tests.out` from the test script.

## Dependencies and integration points
It depends on curl, tar, CMake, make, Xcode on macOS, Homebrew, kcov, gflags/snappy/gperftools, Travis-style environment variables, and TiKV test output conventions.

## Risks and edge cases
Downloaded dependencies are unauthenticated archives. Travis-specific variables suggest this may be historical. Coverage parsing from `tests.out` is brittle. The Makefile assumes `LOCAL_DIR` is defined by the caller.

## Test signals
Successful dependency preparation, `CI=true ci-build/test.sh`, and coverage upload/coverage directory generation validate these targets.
